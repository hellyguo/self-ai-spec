#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Java 复杂度热点扫描器（缩进启发式）。

规则（可配置）：
- 行首 tab 数 >= 6，或行首空格数 >= 24；
- 混合缩进按 1 tab = 4 spaces 折算，等效缩进 >= 24 即命中；
- 默认跳过空行、纯注释行、package/import；
- 默认跳过生成的 *Base.java。

用法：
    python3 complexity_scan.py --root /path/to/project
    python3 complexity_scan.py --root . --top 30 --min-lines 100
    python3 complexity_scan.py --root . --format json

说明：这是“热点定位”启发式，不等价于圈复杂度；命中后需人工确认并结合方法级分析。
"""
import argparse
import json
import os
import re
import sys


def leading_ws(line):
    tabs = 0
    spaces = 0
    for ch in line:
        if ch == "\t":
            tabs += 1
        elif ch == " ":
            spaces += 1
        else:
            break
    return tabs, spaces


def is_code_line(stripped):
    if not stripped:
        return False
    if stripped.startswith("//") or stripped.startswith("*") or stripped.startswith("/*"):
        return False
    if stripped.startswith("package ") or stripped.startswith("import "):
        return False
    return True


def scan_file(path, threshold_tabs, threshold_spaces):
    try:
        lines = open(path, "r", encoding="utf-8", errors="ignore").read().splitlines()
    except OSError:
        return None
    high_lines = 0
    max_effective = 0
    blocks = []
    current = None
    for index, line in enumerate(lines, 1):
        tabs, spaces = leading_ws(line)
        effective = tabs * 4 + spaces
        max_effective = max(max_effective, effective)
        hit = (tabs >= threshold_tabs) or (spaces >= threshold_spaces) or (effective >= threshold_spaces)
        if hit and is_code_line(line.strip()):
            high_lines += 1
            if current is None:
                current = {"start": index, "end": index, "maxIndent": effective}
            else:
                current["end"] = index
                current["maxIndent"] = max(current["maxIndent"], effective)
        else:
            if current is not None:
                blocks.append(current)
                current = None
    if current is not None:
        blocks.append(current)
    if not lines:
        return None
    blocks.sort(key=lambda b: (b["maxIndent"], b["end"] - b["start"]), reverse=True)
    return {
        "lines": len(lines),
        "highLines": high_lines,
        "ratio": round(high_lines / float(len(lines)), 4) if lines else 0,
        "maxIndent": max_effective,
        "topBlock": blocks[0] if blocks else None,
        "blocks": blocks[:5],
    }


def main():
    parser = argparse.ArgumentParser(description="Java 复杂度热点扫描器")
    parser.add_argument("--root", default=".", help="项目根目录")
    parser.add_argument("--threshold-tabs", type=int, default=6, help="tab 阈值")
    parser.add_argument("--threshold-spaces", type=int, default=24, help="空格等效阈值")
    parser.add_argument("--min-lines", type=int, default=50, help="最小文件行数")
    parser.add_argument("--top", type=int, default=50, help="Markdown 输出条数")
    parser.add_argument("--exclude", action="append", default=[], help="排除 glob，可重复")
    parser.add_argument("--include-generated", action="store_true", help="包含 *Base.java")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    import fnmatch
    root = os.path.abspath(args.root)
    rows = []
    for dirpath, _, filenames in os.walk(root):
        normalized = dirpath.replace(os.sep, "/")
        if "/src/main/java/" not in normalized or "/target/" in normalized:
            continue
        for name in filenames:
            if not name.endswith(".java"):
                continue
            if not args.include_generated and name.endswith("Base.java"):
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            if any(fnmatch.fnmatch(rel, p) for p in args.exclude):
                continue
            result = scan_file(path, args.threshold_tabs, args.threshold_spaces)
            if not result or result["lines"] < args.min_lines:
                continue
            result["file"] = rel
            result["module"] = rel.split("/")[0]
            rows.append(result)

    rows.sort(key=lambda r: (r["highLines"], r["maxIndent"]), reverse=True)

    if args.format == "json":
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return

    print("# 复杂度热点（缩进启发式：tab>=%d 或等效空格>=%d）\n" % (args.threshold_tabs, args.threshold_spaces))
    print("| 排名 | 文件 | 模块 | 行数 | 高缩进行 | 占比 | 最大缩进 | 最深区块 |")
    print("|---|---|---|---|---|---|---|---|")
    for index, row in enumerate(rows[:args.top], 1):
        block = row["topBlock"]
        block_text = "{}-{}".format(block["start"], block["end"]) if block else "-"
        print("| {} | {} | {} | {} | {} | {}% | {} | {} |".format(
            index, row["file"], row["module"], row["lines"], row["highLines"],
            round(row["ratio"] * 100, 1), row["maxIndent"], block_text))
    print("\n命中文件数：{}。".format(len(rows)))
    total_high = sum(r["highLines"] for r in rows)
    print("高缩进行总数：{}。".format(total_high))


if __name__ == "__main__":
    sys.exit(main())
