# arena_walk.py —— 无 libc 符号时遍历 glibc arena 链
#
# 用法（core 上）：
#   gdb -q -batch -ex 'source arena_walk.py' \
#       -ex 'arena_walk --glibc 2.28 <arena_base>' ./app core
#   或先设置： set $ma = <arena_base>
#             arena_walk --glibc 2.28
#   版本也可用环境变量：ARENA_GLIBC=2.31 gdb ...
#
# 说明：
#   - 偏移表：
#       <= 2.25 : top=0x58, next=0x868, attached=0x878, system_mem=0x880
#       2.26-2.31: top=0x60, next=0x870, attached=0x880, system_mem=0x888
#     2.32+ 布局可能变化，脚本会警告并使用 2.26-2.31 表，需人工核对。
#   - 不传 --glibc 时默认 2.26-2.31，并打印“未声明版本”的提示。
#   - 地址可用 gdb 表达式（如 `<hit_addr>-0x60`）。
#
# 如何得到初始 arena（无符号）：
#   1) 从堆尾找到 top chunk 的地址值（<top_value>）；
#   2) 在 libc RW 数据段里 `find /g <rw_start>, <rw_end>, <top_value>`；
#   3) 命中地址 − 0x60 即 arena 基址；把它传给本脚本。
#
# 带 MemoryError 处理：core 缺页/坏地址时不会把 gdb 打断。

import gdb
import os

TABLES = {
    "old": {"label": "<=2.25", "top": 0x58, "next": 0x868,
            "attached": 0x878, "sysmem": 0x880, "maxsysmem": 0x888},
    "new": {"label": "2.26-2.31", "top": 0x60, "next": 0x870,
            "attached": 0x880, "sysmem": 0x888, "maxsysmem": 0x890},
}


def _parse_version(s):
    """'2.28' -> (2, 28)；解析失败返回 None。"""
    try:
        parts = s.strip().split(".")
        return int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
    except (ValueError, IndexError):
        return None


def _pick_table(ver):
    """返回 (offset_table, warning_or_None)。"""
    if not ver:
        return TABLES["new"], ("no --glibc given; assuming 2.26-2.31 offsets "
                               "(pass --glibc <ver> if unsure)")
    v = _parse_version(ver)
    if v is None:
        return TABLES["new"], "cannot parse --glibc %r; assuming 2.26-2.31" % ver
    if v <= (2, 25):
        return TABLES["old"], None
    if v <= (2, 31):
        return TABLES["new"], None
    return TABLES["new"], ("glibc %s offsets are not verified; using 2.26-2.31 "
                           "table, please cross-check with debug symbols" % ver)


def _q(inf, addr, size=8):
    try:
        return int.from_bytes(inf.read_memory(addr, size).tobytes(), "little")
    except gdb.MemoryError:
        return None


class ArenaWalk(gdb.Command):
    """arena_walk [--glibc <ver>] [arena_addr] — walk glibc arenas (no symbols required)."""

    def __init__(self):
        super(ArenaWalk, self).__init__("arena_walk", gdb.COMMAND_DATA)

    def _parse(self, arg):
        ver = os.environ.get("ARENA_GLIBC")
        toks = arg.split()
        rest = []
        i = 0
        while i < len(toks):
            t = toks[i]
            if t == "--glibc" and i + 1 < len(toks):
                ver = toks[i + 1]
                i += 2
                continue
            if t.startswith("--glibc="):
                ver = t.split("=", 1)[1]
                i += 1
                continue
            rest.append(t)
            i += 1
        return ver, " ".join(rest)

    def invoke(self, arg, from_tty):
        inf = gdb.selected_inferior()
        ver, expr = self._parse(arg)
        table, warn = _pick_table(ver)
        print("arena_walk: glibc=%s offsets=%s" %
              (ver if ver else "unset", table["label"]))
        if warn:
            print("WARNING: %s" % warn)

        if expr:
            try:
                start = int(gdb.parse_and_eval(expr))
            except Exception as e:
                print("bad address expression: %s" % e)
                return
        else:
            try:
                start = int(gdb.parse_and_eval("(unsigned long)&main_arena"))
            except Exception:
                print("usage: arena_walk [--glibc <ver>] <arena_addr>")
                return

        print("%-4s %-18s %-12s %-16s %-10s" %
              ("idx", "arena", "sysmem_MB", "top", "threads"))
        a = start
        warned = False
        for i in range(64):
            sysmem = _q(inf, a + table["sysmem"])
            top = _q(inf, a + table["top"])
            nxt = _q(inf, a + table["next"])
            thr = _q(inf, a + table["attached"])
            if sysmem is None or top is None:
                print("%-4d 0x%016x  <unreadable>" % (i, a))
                return
            # 合理性检查：偏移不匹配时通常读出荒谬值
            if not warned and (sysmem > (1 << 48) or top < 0x10000 or
                               (top & 0x7) != 0):
                print("WARNING: implausible field values (system_mem=0x%x top=0x%x); "
                      "offsets may not match this glibc, retry with --glibc <ver>"
                      % (sysmem, top))
                warned = True
            print("%-4d 0x%016x %-12.1f 0x%-14x %-10s"
                  % (i, a, sysmem / 1048576.0, top,
                     thr if thr is not None else "?"))
            if nxt is None or nxt == 0:
                print("chain end (next=0)")
                return
            if nxt == start:
                print("closed loop at idx %d" % i)
                return
            a = nxt
        print("stopped after 64 arenas (possible corruption)")


ArenaWalk()
print("arena_walk loaded: run `arena_walk [--glibc <ver>] <arena_addr>`")
