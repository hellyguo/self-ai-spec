---
name: code-detect-dup
description: "该skill提供了一份simian执行样例，借鉴此样例，完成对代码的重复度检查"
---

```bash
#!/bin/bash

threshold=80

java_list="$(~/.cargo/bin/fd -t f -e java | grep -v "\/test\/" | xargs)"

java -jar ~/app/simian/simian-4.2.1.jar -language=java -threshold=${threshold} $java_list
```

1. 其中，threshold应根据实际情况调整
2. 其中，language=java应根据实际情况调整

