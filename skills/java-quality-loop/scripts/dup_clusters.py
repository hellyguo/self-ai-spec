#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完全重复类簇扫描器（代码质量循环专用）。

对 Java 源码做“去 package 归一化”后按内容哈希分组，输出完全一致的重复类簇，
并按类型（接口/静态状态/无状态）做初步风险分类。

用法：
    python3 dup_clusters.py --root /path/to/project
    python3 dup_clusters.py --root . --min-lines 80 --min-copies 2
    python3 dup_clusters.py --root . --exclude "**/count/**" --format json

设计原则：
- 只使用标准库，无外部依赖。
- 只报告“完全一致”的簇，避免把相似但已分叉的代码误判为可机械合并。
- 分类结果仅为提示，最终由人工按 skill 的决策树确认。
"""
import argparse
import hashlib
import json
import os
import re
import sys


def normalize(text):
    """去掉 package 声明与行尾差异，保留其余内容用于一致性比较。"""
    text = text.replace("\r\n", "\n")
    return re.sub(r"^\s*package\s+[\w.]+;\s*", "", text, count=1, flags=re.M)


def classify(source):
    """粗略分类：接口 / 静态状态 / 无状态。"""
    if re.search(r"public\s+interface\s+", source):
        return "interface"
    if re.search(r"static\s+(?!final)[A-Za-z0-9_<>, ]+\s+\w+\s*=", source):
        return "static-state"
    if re.search(r"static\s+final\s+(Map|List|Set|HashMap|ArrayList|LinkedList)\b", source):
        return "static-state"
    return "stateless"


def matches_any(path, patterns):
    import fnmatch
    return any(fnmatch.fnmatch(path, p) for p in patterns)


def scan(root, min_lines, min_copies, excludes):
    groups = {}
    for dirpath, _, filenames in os.walk(root):
        if "/src/main/java/" not in dirpath.replace(os.sep, "/"):
            continue
        if "/target/" in dirpath.replace(os.sep, "/"):
            continue
        for name in filenames:
            if not name.endswith(".java"):
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            if matches_any(rel, excludes):
                continue
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                    source = fh.read()
            except OSError:
                continue
            normalized = normalize(source)
            lines = normalized.count("\n") + 1
            if lines < min_lines:
                continue
            digest = hashlib.md5(normalized.encode("utf-8")).hexdigest()
            groups.setdefault((name, digest), []).append((rel, lines, source))

    clusters = []
    for (name, digest), items in groups.items():
        if len(items) < min_copies:
            continue
        lines = items[0][1]
        kind = classify(items[0][2])
        clusters.append({
            "name": name,
            "lines": lines,
            "copies": len(items),
            "score": lines * len(items),
            "kind": kind,
            "paths": [item[0] for item in items],
            "digest": digest,
        })
    clusters.sort(key=lambda item: item["score"], reverse=True)
    return clusters


def render_markdown(clusters, top):
    print("# 完全重复类簇（去 package 归一化）\n")
    print("| 排名 | 类名 | 行数 | 副本 | 评分 | 类型 | 路径 |")
    print("|---|---|---|---|---|---|---|")
    for index, cluster in enumerate(clusters[:top], 1):
        paths = "<br>".join(cluster["paths"])
        print("| {} | {} | {} | {} | {} | {} | {} |".format(
            index, cluster["name"], cluster["lines"], cluster["copies"],
            cluster["score"], cluster["kind"], paths))
    print("\n总计：{} 个完全重复簇。".format(len(clusters)))
    stateless = sum(1 for c in clusters if c["kind"] == "stateless")
    interfaces = sum(1 for c in clusters if c["kind"] == "interface")
    states = sum(1 for c in clusters if c["kind"] == "static-state")
    print("分类：无状态 {}，接口 {}，静态状态 {}。".format(stateless, interfaces, states))


def main():
    parser = argparse.ArgumentParser(description="完全重复类簇扫描器")
    parser.add_argument("--root", default=".", help="项目根目录")
    parser.add_argument("--min-lines", type=int, default=80, help="最小行数阈值")
    parser.add_argument("--min-copies", type=int, default=2, help="最小副本数")
    parser.add_argument("--top", type=int, default=50, help="Markdown 输出条数")
    parser.add_argument("--exclude", action="append", default=[],
                        help="排除的 glob，可重复，例如 --exclude '**/count/**'")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    clusters = scan(os.path.abspath(args.root), args.min_lines, args.min_copies, args.exclude)
    if args.format == "json":
        print(json.dumps(clusters, ensure_ascii=False, indent=2))
    else:
        render_markdown(clusters, args.top)


if __name__ == "__main__":
    sys.exit(main())
