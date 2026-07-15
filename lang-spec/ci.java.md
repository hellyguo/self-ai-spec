# Java 构建工具

相关工具路径，见 skill /java-env
首选 mvnd，次选 mvn

## 构建/测试命令

```bash
# 编译项目
mvn compile

# 运行所有测试
mvn test

# 运行单个测试类
mvn test -Dtest=XxxTest

# 运行单个测试方法
mvn test -Dtest=XxxTest#testYyy

# 打包（跳过测试）
mvn package -DskipTests

# 清理并编译
mvn clean compile

# 完整构建流程
mvn clean test package
```
