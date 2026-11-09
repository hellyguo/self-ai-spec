#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""分派链与重复构造范式扫描器（Java 质量循环专用）。

用于发现两类“相似范式”候选：
1. 结构分派：switch/else-if 分支密集的类；
2. 重复构造：同一构造调用在多个文件中反复出现。

用法：
    python3 pattern_scan.py --root /path/to/project
    python3 pattern_scan.py --root . --min-cases 8 --top 30
    python3 pattern_scan.py --root . --construct "new SimpleDateFormat(" --format json

设计原则：
- 只使用标准库。
- 输出候选与计数，不自动判定“必须重构”；最终由决策树与人工确认。
"""
import argparse
import json
import os
import re
import sys


DEFAULT_CONSTRUCTS = [
    "new SimpleDateFormat(",
    "new DecimalFormat(",
    "new GregorianCalendar(",
]


def scan_dispatch(root, min_cases):
    rows = []
    for dirpath, _, filenames in os.walk(root):
        normalized_dir = dirpath.replace(os.sep, "/")
        if "/src/main/java/" not in normalized_dir or "/target/" in normalized_dir:
            continue
        for name in filenames:
            if not name.endswith(".java"):
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            try:
                source = open(path, "r", encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            switch_count = len(re.findall(r"\bswitch\s*\(", source))
            case_count = len(re.findall(r"\bcase\s+", source))
            else_if_count = len(re.findall(r"\belse\s+if\s*\(", source))
            equals_count = len(re.findall(r"\.equals\s*\(", source))
            score = case_count + else_if_count
            if score >= min_cases:
                rows.append({
                    "file": rel,
                    "module": rel.split("/")[0],
                    "switch": switch_count,
                    "case": case_count,
                    "elseIf": else_if_count,
                    "equals": equals_count,
                    "score": score,
                })
    rows.sort(key=lambda item: item["score"], reverse=True)
    return rows


def scan_constructs(root, patterns):
    stats = {}
    for pattern in patterns:
        total = 0
        modules = {}
        for dirpath, _, filenames in os.walk(root):
            normalized_dir = dirpath.replace(os.sep, "/")
            if "/src/main/java/" not in normalized_dir or "/target/" in normalized_dir:
                continue
            for name in filenames:
                if not name.endswith(".java"):
                    continue
                path = os.path.join(dirpath, name)
                rel = os.path.relpath(path, root).replace(os.sep, "/")
                try:
                    source = open(path, "r", encoding="utf-8", errors="ignore").read()
                except OSError:
                    continue
                count = source.count(pattern)
                if count:
                    total += count
                    module = rel.split("/")[0]
                    modules[module] = modules.get(module, 0) + count
        stats[pattern] = {"total": total, "modules": modules}
    return stats


def render_markdown(rows, stats, top):
    print("# 分派链候选（按 case + else-if 排序）\n")
    print("| 排名 | 文件 | 模块 | switch | case | else-if | equals | 评分 |")
    print("|---|---|---|---|---|---|---|---|")
    for index, row in enumerate(rows[:top], 1):
        print("| {} | {} | {} | {} | {} | {} | {} | {} |".format(
            index, row["file"], row["module"], row["switch"], row["case"],
            row["elseIf"], row["equals"], row["score"]))
    print("\n分派候选总数：{}。\n".format(len(rows)))

    print("## 重复构造范式\n")
    print("| 构造 | 总数 | 模块分布 |")
    print("|---|---|---|")
    for pattern, data in stats.items():
        modules = ", ".join("{}={}".format(k, v) for k, v in
                            sorted(data["modules"].items(), key=lambda x: -x[1])[:8])
        print("| `{}` | {} | {} |".format(pattern, data["total"], modules))


def main():
    parser = argparse.ArgumentParser(description="分派链与重复构造范式扫描器")
    parser.add_argument("--root", default=".", help="项目根目录")
    parser.add_argument("--min-cases", type=int, default=5, help="最小分支数阈值")
    parser.add_argument("--top", type=int, default=50, help="Markdown 输出条数")
    parser.add_argument("--construct", action="append", default=[],
                        help="重复构造模式，可重复；默认包含常见 JDK 构造")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    patterns = args.construct if args.construct else DEFAULT_CONSTRUCTS
    rows = scan_dispatch(root, args.min_cases)
    stats = scan_constructs(root, patterns)

    if args.format == "json":
        print(json.dumps({"dispatch": rows, "constructs": stats}, ensure_ascii=False, indent=2))
    else:
        render_markdown(rows, stats, args.top)


if __name__ == "__main__":
    sys.exit(main())
