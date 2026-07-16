# PMD自定义规则集模板

```xml
<?xml version="1.0"?>
<ruleset name="Custom Java Rules"
         xmlns="http://pmd.sourceforge.net/ruleset/2.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://pmd.sourceforge.net/ruleset/2.0.0 
                             http://pmd.sourceforge.net/ruleset_2_0_0.xsd">
    
    <description>自定义Java代码检查规则集</description>
    
    <!-- 包含基础规则 -->
    <rule ref="rulesets/java/basic.xml"/>
    
    <!-- 包含代码风格规则，但排除特定规则 -->
    <rule ref="rulesets/java/codeestyle.xml">
        <exclude name="ShortVariable"/>
        <exclude name="OnlyOneReturn"/>
    </rule>
    
    <!-- 包含设计规则，自定义复杂度阈值 -->
    <rule ref="rulesets/java/design.xml/CyclomaticComplexity">
        <properties>
            <property name="reportLevel" value="15"/>  <!-- 默认10 -->
        </properties>
    </rule>
    
    <!-- 自定义规则组合 -->
    <rule ref="rulesets/java/basic.xml/EmptyCatchBlock"/>
    <rule ref="rulesets/java/codeestyle.xml/LongVariable"/>
    <rule ref="rulesets/java/design.xml/GodClass"/>
    <rule ref="rulesets/java/security.xml/HardCodedCryptoKey"/>
</ruleset>
```
