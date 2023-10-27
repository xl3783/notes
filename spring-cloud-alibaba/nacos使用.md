# Nacos

使用nacos的配置管理与服务注册发现功能

## 环境准备

- docker环境(示例使用Docker Desktop)
- Nacos镜像
  - `docker pull nacos/nacos-server`
  - mac(m1 m2) 拉取镜像时需要配置
    - `--platform linux/amd64`
    - 不然会报错
      - `no matching manifest for linux/arm64/v8 in the manifest list entries`
    - ![Alt text](assets/nacos%E4%BD%BF%E7%94%A8/image.png)
  - `docker run --name nacos -d -p 8848:8848 -p 9848:9848 -p 9849:9849 -e MODE=standalone nacos/nacos-server:v2.2.3-slim`
- java 17
- postman (验证结果使用,也可以使用网页请求或其他工具)


## 项目搭建

Spring Cloud Alibaba作为一个微服务架构，往往会创建一个父工程管理整个项目的依赖关系。每个子项目代表一个微服务，可以各自选择所需的组件进行使用。

因此，搭建Spring Cloud Alibaba项目总的来说包括两个步骤：

创建父工程，统一管理全局微服务依赖。
创建子服务，引入所需的组件进行业务开发。

### 1. 创建父项目

- 创建maven项目
- 设置依赖
```xml
<properties>
      <maven.compiler.source>17</maven.compiler.source>
      <maven.compiler.target>17</maven.compiler.target>
      <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
      <spring-boot.version>3.0.12</spring-boot.version>
      <spring-cloud.version>2022.0.1</spring-cloud.version>
      <spring-cloud-alibaba.version>2022.0.0.0-RC1</spring-cloud-alibaba.version>
</properties>

<!--    不使用父pom,我们在dependencyManagement引入依赖配置, 主要是spring boot、 spring cloud 和 spring cloud alibaba-->
   <dependencyManagement>
      <dependencies>
         <dependency>
               <groupId>org.springframework.cloud</groupId>
               <artifactId>spring-cloud-dependencies</artifactId>
               <version>${spring-cloud.version}</version>
               <type>pom</type>
               <scope>import</scope>
         </dependency>
         <!-- Spring Cloud Alibaba -->
         <dependency>
               <groupId>com.alibaba.cloud</groupId>
               <artifactId>spring-cloud-alibaba-dependencies</artifactId>
               <version>${spring-cloud-alibaba.version}</version>
               <type>pom</type>
               <scope>import</scope>
         </dependency>
         <!-- https://mvnrepository.com/artifact/org.springframework.boot/spring-boot-dependencies -->
         <dependency>
               <groupId>org.springframework.boot</groupId>
               <artifactId>spring-boot-dependencies</artifactId>
               <version>${spring-boot.version}</version>
               <type>pom</type>
               <scope>import</scope>
         </dependency>

      </dependencies>
   </dependencyManagement>
```

`spring-boot-dependencies`管理着`Spring Boot`各个starter的对应版本，`spring-cloud-dependencies`管理着S`pring Cloud`各个组件的对应版本，`spring-cloud-alibaba-denpendencies`管理着`Spring Cloud Alibaba`各个组件的对应版本。

在子服务中，引入组件依赖时不必指定版本，会从上述依赖管理中获取对应的版本信息，避免依赖冲突。

### 2. nacos配置管理

- 在父项目下创建子项目`nacos-config`
- 设置pom依赖
```xml
   <dependencies>
<!--         https://mvnrepository.com/artifact/com.alibaba.cloud/spring-cloud-starter-alibaba-nacos-config-->
   <dependency>
         <groupId>com.alibaba.cloud</groupId>
         <artifactId>spring-cloud-starter-alibaba-nacos-config</artifactId>
   </dependency>

   <dependency>
         <groupId>org.springframework.boot</groupId>
         <artifactId>spring-boot-starter-web</artifactId>
   </dependency>

   <dependency>
         <groupId>org.springframework.cloud</groupId>
         <artifactId>spring-cloud-starter-bootstrap</artifactId>
   </dependency>
</dependencies>
```
- 在resources目录下创建`bootstrap.properties`文件
```properties
spring.cloud.nacos.config.server-addr=127.0.0.1:8848
spring.application.name=nacos-config-client
spring.output.ansi.enabled=always
```
- 启动函数
```java
@SpringBootApplication
public class NacosConfigApp {
    public static void main(String[] args) {
        SpringApplication.run(NacosConfigApp.class, args);
    }
}
```

- 创建controller, 从配置中心获取配置
```java
@RestController
@RequestMapping("/config")
@RefreshScope // 添加该注解注解后, 会自动刷新配置
public class ConfigController {

    // 使用@Value从配置中心获取配置
    @Value("${useLocalCache:false}")
    private boolean useLocalCache;

    @RequestMapping("/get")
    public boolean get() {
        return useLocalCache;
    }
}
```

- 启动项目, 访问`http://localhost:8080/config/get`, 返回`false`
- 在nacos配置中心添加配置
  - Data ID: nacos-config-client
  - Group: DEFAULT_GROUP
  - 配置内容: useLocalCache: true
  - ![Alt text](assets/nacos%E4%BD%BF%E7%94%A8/image-2.png)
  - ![Alt text](assets/nacos%E4%BD%BF%E7%94%A8/image-3.png)
- 访问`http://localhost:8080/config/get`, 返回`true`

### 3. Nacos服务注册与发现

#### 在父项目下创建子项目`nacos-discovery`
- 设置pom依赖
```xml
       <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <dependency>
            <groupId>com.alibaba.cloud</groupId>
            <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
        </dependency>

    </dependencies>
```
- 配置文件
```properties
server.port=8070
spring.application.name=service-provider
spring.cloud.nacos.discovery.server-addr=127.0.0.1:8848
```
- 启动函数
```java
@SpringBootApplication
@EnableDiscoveryClient // 使用该注解,则该服务会自动注册到Nacos中
public class NacosProviderApplication {

	public static void main(String[] args) {
		SpringApplication.run(NacosProviderApplication.class, args);
	}

	@RestController
	class EchoController {
		@RequestMapping(value = "/echo/{string}", method = RequestMethod.GET)
		public String echo(@PathVariable String string) {
			return "Hello Nacos Discovery " + string;
		}
	}
}
```
- 启动项目, 访问`http://localhost:8070/echo/123`, 返回`Hello Nacos Discovery 123`
- 在nacos服务管理中查看服务
  ![Alt text](assets/nacos%E4%BD%BF%E7%94%A8/image-5.png)

#### 在父项目下创建子项目`nacos-consumer`
- 设置pom依赖
```xml
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>com.alibaba.cloud</groupId>
            <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-loadbalancer</artifactId>
        </dependency>
    </dependencies>
```
- 配置文件
```properties
server.port=8090
spring.application.name=service-consumer
spring.cloud.nacos.discovery.server-addr=127.0.0.1:8848
```
- 启动函数
```java
@SpringBootApplication
@EnableDiscoveryClient
public class NacosConsumerApplication {

    // 使用@LoadBalanced注解,一定要添加对应的pom依赖:spring-cloud-loadbalancer(不添加依赖ide不会报错)
    // 若不添加依赖,则无法直接使用Nacos中所注册的服务名进行动态路由
    @LoadBalanced
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }

    public static void main(String[] args) {
        SpringApplication.run(NacosConsumerApplication.class, args);
    }

    @RestController
    public class TestController {

        private final RestTemplate restTemplate;

        @Autowired
        public TestController(RestTemplate restTemplate) {this.restTemplate = restTemplate;}

        @RequestMapping(value = "/echo/{str}", method = RequestMethod.GET)
        public String echo(@PathVariable String str) {
            return restTemplate.getForObject("http://service-provider/echo/" + str, String.class);
        }
    }
}
```
- 启动项目, 访问`http://localhost:8090/echo/123`, 返回`Hello Nacos Discovery 123`
- 在nacos服务管理中查看服务
  ![Alt text](assets/nacos%E4%BD%BF%E7%94%A8/image-6.png)


## 问题

1. No spring.config.import set 
   ![Alt text](assets/nacos%E4%BD%BF%E7%94%A8/image-1.png)

- 解决方法
  - 引入pom依赖
   ```
   <dependency>
      <groupId>org.springframework.cloud</groupId>
      <artifactId>spring-cloud-starter-bootstrap</artifactId>
   </dependency>
   ```
2. springboot 启动报错(Unsupported class file major version 61)
   
   spring-boot-dependencies 版本与jdk不匹配,当使用高版本java时,对应的springboot版本也要高
- 解决方法
  - 更换Springboot版本至`3.0.12`,以适配`java 17`

3. 502 Bad Gateway: [no body]] with root cause
   无法访问(在本demo中为域名解析失败)
   ![Alt text](assets/nacos%E4%BD%BF%E7%94%A8/image-4.png)
- 原因
  使用@LoadBalanced注解,一定要添加对应的pom依赖:spring-cloud-loadbalancer(不添加依赖ide不会报错),若不添加依赖,则无法直接使用Nacos中所注册的服务名进行动态路由.
- 解决方法
  - 引入pom依赖
   ```
   <dependency>
      <groupId>org.springframework.cloud</groupId>
      <artifactId>spring-cloud-starter-bootstrap</artifactId>
   </dependency>
   ```

