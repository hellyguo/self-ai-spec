# PMD构建工具集成模板

## Maven集成

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-pmd-plugin</artifactId>
    <version>3.20.0</version>
    <configuration>
        <rulesets>
            <ruleset>rulesets/java/quickstart.xml</ruleset>
            <ruleset>custom-ruleset.xml</ruleset>
        </rulesets>
        <failurePriority>3</failurePriority>
        <minimumTokens>100</minimumTokens>
        <linkXRef>false</linkXRef>
    </configuration>
    <executions>
        <execution>
            <phase>verify</phase>
            <goals>
                <goal>check</goal>
                <goal>cpd-check</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

## Gradle集成

```groovy
plugins {
    id 'pmd'
}

pmd {
    toolVersion = '6.19.0'
    ruleSets = []
    ruleSetFiles = files("custom-ruleset.xml")
    ignoreFailures = false
    consoleOutput = true
}

pmdMain {
    ruleSets = ['rulesets/java/quickstart.xml']
}

pmdTest {
    ruleSets = ['rulesets/java/basic.xml']
}
```
