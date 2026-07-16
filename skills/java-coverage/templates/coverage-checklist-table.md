# 增量覆盖完整性校验清单模板

| 源文件 | 是否需测试 | 测试文件名 | 备注 |
| -------- | ----------- | ----------- | ------ |
| XxxEnum.java | 是 | XxxEnumTest.java | 枚举类 |
| XxxService.java | 是 | XxxServiceTest.java | Mockito模拟依赖 |
| XxxDao.java | 是 | XxxDaoTest.java | 接口新增方法用Mockito验证 |
| Xxx.xml | 否 | - | 非源代码文件，跳过 |
