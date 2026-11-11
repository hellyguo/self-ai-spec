# arena_walk.py —— 无 libc 符号时遍历 glibc arena 链
#
# 用法（core 上）：
#   gdb -q -batch -ex 'source arena_walk.py' -ex 'arena_walk <arena_base>' ./app core
#   或先设置： set $ma = <arena_base>
#             arena_walk
#
# 说明：
#   - 偏移按 glibc 2.26–2.31（64-bit）：top=0x60, next=0x870,
#     attached_threads=0x880, system_mem=0x888, max_system_mem=0x890。
#   - 2.32+ / 更老版本请改下面的常量（见 references/glibc-offsets.md）。
#   - 地址可用 gdb 表达式（如 `<hit_addr>-0x60`）。
#
# 如何得到初始 arena（无符号）：
#   1) 从堆尾找到 top chunk 的地址值（<top_value>）；
#   2) 在 libc RW 数据段里 `find /g <rw_start>, <rw_end>, <top_value>`；
#   3) 命中地址 − 0x60 即 arena 基址；把它传给本脚本。
#
# 带 MemoryError 处理：core 缺页/坏地址时不会把 gdb 打断。

import gdb

OFF_TOP = 0x60
OFF_NEXT = 0x870
OFF_ATTACHED = 0x880
OFF_SYSMEM = 0x888
OFF_MAXSYSMEM = 0x890


def _q(inf, addr, size=8):
    try:
        return int.from_bytes(inf.read_memory(addr, size).tobytes(), "little")
    except gdb.MemoryError:
        return None


class ArenaWalk(gdb.Command):
    """arena_walk [arena_addr] — walk glibc arenas (no symbols required)."""

    def __init__(self):
        super(ArenaWalk, self).__init__("arena_walk", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        inf = gdb.selected_inferior()
        arg = arg.strip()
        if arg:
            try:
                start = int(gdb.parse_and_eval(arg))
            except Exception as e:
                print("bad address expression: %s" % e)
                return
        else:
            try:
                start = int(gdb.parse_and_eval("(unsigned long)&main_arena"))
            except Exception:
                print("usage: arena_walk <arena_addr>   (e.g. arena_walk <hit_addr-0x60>)")
                return

        print("%-4s %-18s %-12s %-16s %-10s" % ("idx", "arena", "sysmem_MB", "top", "threads"))
        a = start
        for i in range(64):
            sysmem = _q(inf, a + OFF_SYSMEM)
            top = _q(inf, a + OFF_TOP)
            nxt = _q(inf, a + OFF_NEXT)
            thr = _q(inf, a + OFF_ATTACHED)
            if sysmem is None or top is None:
                print("%-4d 0x%016x  <unreadable>" % (i, a))
                return
            print("%-4d 0x%016x %-12.1f 0x%-14x %-10s"
                  % (i, a, sysmem / 1048576.0, top, thr if thr is not None else "?"))
            if nxt is None or nxt == 0:
                print("chain end (next=0)")
                return
            if nxt == start:
                print("closed loop at idx %d" % i)
                return
            a = nxt
        print("stopped after 64 arenas (possible corruption)")


ArenaWalk()
print("arena_walk loaded: run `arena_walk <arena_addr>`")
