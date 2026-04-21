---
name: code-detect-dup
description: "该skill提供了一份simian执行样例，借鉴此样例，完成对代码的重复度检查"
---

```bash
#!/bin/bash

java -jar ~/app/simian/simian-4.2.1.jar -language=java -threshold=5 $(fd0 -t f -e java | grep0 -v "\/test\/" | xargs) > docs/dup-{yyyy-mm-dd}-{seq}.txt 2>&1

```

1. 其中，threshold应根据实际情况调整
2. 其中，language=java应根据实际情况调整
3. 其中的 fd0/grep0 可通过bash/zsh 的 alias 查看其原始命令
4. seq应从001开始，按日重置，dup-{yyyy-mm-dd}-{seq}.txt 最终应 git 留档

