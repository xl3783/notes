# Mybatis-plus 学习

## 初始化Spring项目
- 创建maven项目
- 添加依赖(pom.xml)
```xml
<dependencies>
    <!-- https://mvnrepository.com/artifact/org.springframework.boot/spring-boot-starter -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter</artifactId>
        <version>3.1.2</version>
    </dependency>
    <!-- https://mvnrepository.com/artifact/org.springframework.boot/spring-boot-starter-test -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <version>3.1.0</version>
        <scope>test</scope>
    </dependency>
    <!-- https://mvnrepository.com/artifact/org.springframework.boot/spring-boot-starter-web -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
        <version>3.1.2</version>
    </dependency>
    <!-- https://mvnrepository.com/artifact/org.slf4j/slf4j-api -->
    <dependency>
        <groupId>org.slf4j</groupId>
        <artifactId>slf4j-api</artifactId>
        <version>2.0.7</version>
    </dependency>
</dependencies>
```
- 创建启动类
```java
package org.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```
- 创建controller
```java
package org.example.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class Hello {
    @GetMapping("/hello")
    public String hello(@RequestParam(value = "name", defaultValue = "World") String name) {
        return String.format("Hello %s!", name);
    }
}
```
- 启动项目,在浏览器中输入`http://localhost:8080/hello?name=Mybatis`即可看到`Hello Mybatis!`的输出

## 增加mybatis-plus依赖

- 安装h2数据库(也可以自己安装别的数据库)
  - h2数据库可以当作内存数据库,用来做单元测试很方便
  - 添加 pom 依赖
  - ```xml
    <dependency>
        <groupId>com.h2database</groupId>
        <artifactId>h2</artifactId>
        <version>1.4.200</version>
        <scope>test</scope>
    </dependency>
    ```
  - 在`src/main/resources`目录下创建`application.yml`文件,添加如下配置
    - ```yaml
        spring:
            datasource:
                driver-class-name: org.h2.Driver
                url: jdbc:h2:mem:test
                username: sa
                password: 123456
              h2:
                console:
                    enabled: true # 开启控制台
        ```
    - 启动项目,在浏览器中输入`http://localhost:8080/h2-console`即可进入h2控制台
- 添加mybatis-plus依赖
  ```xml
    <dependency>
        <groupId>com.baomidou</groupId>
        <artifactId>mybatis-plus-boot-starter</artifactId>
        <version>3.5.3.1</version>
    </dependency>
  ```