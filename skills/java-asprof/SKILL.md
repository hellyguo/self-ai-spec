---
name: java-asprof
description: "该skill没有执行文件，为操作指引：采集Java执行情况"
---

# 代码编译

1. 通过skill: java-env确定jdk版本，确定mvnd/mvn版本
2. 通过asprof进行采集，路径在 /home/helly/app/async-profiler
3. 命令可参考

```shell

#Basic events:
#  cpu
#  alloc
#  lock
#  wall
#  itimer
#  ctimer

asprof -i 1000 -e $2 -d $wait_time -f /tmp/profile.html $(jps | grep $1 | cut -d" " -f 1)
#asprof -i 1000 -e $2 -t -d $wait_time -f /tmp/profile.html $(jps | grep $1 | cut -d" " -f 1)
#asprof -i 1000 -e $2 -t -d $wait_time --cstack dwarf -f /tmp/profile.html $(jps | grep $1 | cut -d" " -f 1)
#asprof -e $2 -t -d 60 -f /tmp/profile.html $(ps | grep $1 | grep -v grep | sed 's/\t/ /g' | tr -s ' ' | cut -d' ' -f 2)
```

