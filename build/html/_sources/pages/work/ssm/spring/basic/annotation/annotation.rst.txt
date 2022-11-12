IOC/DI注解开发
===========================

Spring的IOC/DI对应的配置使用起来比较复杂，复杂的地方在 **配置文件**

Spring的注解开发用于简化开发

注解开发定义bean
---------------------------

1. 删除原XML配置

2. 类上添加注解

   .. code-block:: java

      @Component("bookDao")
      public class BookDaoImpl implements BookDao {
          public void save() {
              System.out.println("book dao save ..." );
          }
      }

   .. attention::

      注意: ``@Component`` 注解不可以添加在接口上，因为接口是无法创建对象的。

   **XML与注解配置的对应关系**

   .. figure:: images/1.jpg
      :figclass: align-center

3. 配置Spring的注解包扫描

   .. code:: xml

      <context:component-scan base-package="com.linzzz"/>


   .. note::

      base-package指定Spring框架扫描的包路径，它会扫描指定包及其子包中的所有类上的注解。

      * 包路径越多[如:com.linzzz.dao.impl]，扫描的范围越小速度越快

      ..

      * 包路径越少[如:com.linzzz],扫描的范围越大速度越慢

      ..

      * 一般扫描到项目的组织名称即Maven的groupId下[如:com.linzzz]即可。

4. 运行程序

.. note::

   **说明:**

   * BookServiceImpl类没有起名称，所以在App中是按照类型来获取bean对象

   * @Component注解如果不起名称，会有一个默认值就是 **当前类名首字母小写** ，所以也可以按照名称获取，如

   .. code-block:: java

      BookService bookService = (BookService)ctx.getBean("bookServiceImpl");

   对于@Component注解，还衍生出了其他三个注解 ``@Controller``（表现层） 、 ``@Service`` （业务层）、 ``@Repository`` （数据层）

   .. figure:: images/2.jpg
      :figclass: align-center

纯注解开发模式
-------------------------------

将配置文件applicationContext.xml删除掉，使用类来替换。

1. 创建配置类

   .. code-block:: java

      public class SpringConfig {
      }

2. 标识该类为配置类

   在配置类上添加 ``@Configuration`` 注解，将其标识为一个配置类,替换 ``applicationContext.xml``

   .. code-block:: java

      @Configuration
      public class SpringConfig {
      }

3. 用注解替换包扫描配置

   在配置类上添加包扫描注解 ``@ComponentScan`` 替换 ``<context:component-scan base-package=""/>``

   .. code-block:: java

      @Configuration
      @ComponentScan("com.linzzz")
      public class SpringConfig {
      }

4. 创建并执行

   .. code-block:: java

      ApplicationContext ctx = new AnnotationConfigApplicationContext(SpringConfig.class)

.. note::

   1. Java类替换Spring核心配置文件

      .. figure:: images/3.jpg
         :figclass: align-center

   2. ``@Configuration`` 注解用于设定当前类为配置类

   3. ``@ComponentScan`` 注解用于设定扫描路径，( **此注解只能添加一次，多个数据请用数组格式** )

      .. code:: xml

         @ComponentScan({com.linzzz.service","com.linzzz.dao"})

   4. 读取Spring核心配置文件初始化容器对象切换为读取Java配置类初始化容器对象

      注意， 类由 ``ClassPathXmlApplicationContext`` 换成了 ``AnnotationConfigApplicationContext``

      .. code-block:: java

         //加载配置文件初始化容器
         ApplicationContext ctx = new ClassPathXmlApplicationContext("applicationContext.xml");

         //加载配置类初始化容器
         ApplicationContext ctx = new AnnotationConfigApplicationContext(SpringConfig.class);


注解开发bean作用范围与生命周期管理
---------------------------------------------------------

1. 在对应的方法上添加`@PostConstruct`和`@PreDestroy`注解即可

   .. code-block:: java

      //在构造方法之后执行，替换 init-method
       @PostConstruct
       public void init() {
           System.out.println("init ...");
       }

      //在销毁方法之前执行,替换 destroy-method
       @PreDestroy
       public void destroy() {
           System.out.println("destroy ...");
       }

.. attention::

   1. 从JDK9以后jdk中的javax.annotation包被移除了，这两个注解刚好就在这个包中。

      需要导入下面的jar包

      .. code:: xml

         <dependency>
           <groupId>javax.annotation</groupId>
           <artifactId>javax.annotation-api</artifactId>
           <version>1.3.2</version>
         </dependency>

   2. 销毁方法必须是单例才能执行，非单例不执行销毁方法

注解开发依赖注入
-------------------------------

1. 注解实现按照类型注入

   在BookServiceImpl类的bookDao属性上添加 ``@Autowired`` 注解

   .. code-block:: java

      @Autowired
      private BookDao bookDao;

   .. attention::

      1. @Autowired可以写在属性上，也可也写在setter方法上，最简单的处理方式是 **写在属性上并将setter方法删除**

      2. 自动装配基于反射设计创建对象并通过暴力反射为私有属性进行设值，所以此处无需提供setter方法。

2. 注解实现按照名称注入

   对应接口如果有多个实现类，比如添加BookDaoImpl2，此时，按照类型注入就无法区分到底注入哪个对象。

   使用 ``@Qualifier`` 注解 填入注入的bean的名称

   **按照名称注入**

   .. code-block:: java

       @Autowired
       @Qualifier("bookDao1")
       private BookDao bookDao;

   **@Qualifier不能独立使用，必须和@Autowired一起使用**

简单数据类型注入
-----------------------------------

1. 按值注入

   使用 ``@Value`` 注解，将值写入注解的参数中

   注意数据格式要匹配，如将"abc"注入给int值，这样程序就会报错。

   .. code-block:: java

      @Value("itheima")
      private String name;

2. 配置文件注入

   - resource下准备properties文件，如jdbc.properties

      .. code:: xml

         name=zzz

   - 使用注解加载properties配置文件

      在配置类上添加 ``@PropertySource`` 注解

      .. code:: xml

         @Configuration
         @ComponentScan("com.linzzz")
         @PropertySource("jdbc.properties")
         public class SpringConfig {}

   - 使用 ``@Value`` 读取配置文件中的内容

      .. code-block:: java

         @Value("${name}")
         private String name;

   .. attention::

      - 如果读取的properties配置文件有多个，可以使用 ``@PropertySource`` 的属性来指定多个

         .. code:: xml

            @PropertySource({"jdbc.properties","xxx.properties"})

      - ``@PropertySource`` 注解属性中不支持使用通配符 ``*`` ,运行会报错

         .. code:: xml

            @PropertySource({"*.properties"})

      - ``@PropertySource`` 注解属性中可以把 ``classpath:`` 加上,代表从当前项目的根路径找文件

         .. code:: xml

            @PropertySource({"classpath:jdbc.properties"})

IOC/DI注解开发管理第三方bean
--------------------------------------------------------

**使用@Bean注解**

注解开发管理第三方bean
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   1. 在配置类中添加一个方法

      .. code-block:: java

         @Configuration
         public class SpringConfig {
             public DataSource dataSource(){
                 DruidDataSource ds = new DruidDataSource();
                 ds.setDriverClassName("com.mysql.cj.jdbc.Driver");
                 ds.setUrl("jdbc:mysql://localhost:3306/test");
                 ds.setUsername("root");
                 ds.setPassword("123456");
                 return ds;
             }
         }

   2. 在方法上添加 ``@Bean`` 注解

      .. code-block:: java

         @Bean
         public DataSource dataSource(){

      .. note::

         @Bean注解的作用是将方法的返回值制作为Spring管理的一个bean对象

引入外部配置类
~~~~~~~~~~~~~~~~~~~~~~~~~~~

对于数据源的bean,新建一个 ``JdbcConfig`` 配置类存放数据源

.. code-block:: java

   public class JdbcConfig {
      @Bean
       public DataSource dataSource(){
           DruidDataSource ds = new DruidDataSource();
           ds.setDriverClassName("com.mysql.cj.jdbc.Driver");
           ds.setUrl("jdbc:mysql://localhost:3306/test");
           ds.setUsername("root");
           ds.setPassword("123456");
           return ds;
       }
   }

**这个配置类如何能被Spring配置类加载到，并创建DataSource对象在IOC容器中?**

1. 使用包扫描引入

   - 在Spring的配置类上添加包扫描

      .. code-block:: java

         @Configuration
         @ComponentScan("com.linzzz.config")
         public class SpringConfig {

         }

   - 在JdbcConfig上添加配置注解

      .. code-block:: java

         @Configuration
         public class JdbcConfig{
            ...
         }

2. 使用 ``@Import`` 引入

   这种方案可以不用加 ``@Configuration`` 注解，但是必须在Spring配置类上使用 ``@Import`` 注解手动引入需要加载的配置类

   - 去除JdbcConfig类上的注解

      .. code-block:: java

         public class JdbcConfig

   - 在Spring配置类中引入

      .. code-block:: java

         @Configuration
         //@ComponentScan("com.itheima.config")
         @Import({JdbcConfig.class})
         public class SpringConfig {

         }

   .. attention::

      * 扫描注解可以移除

      * @Import参数需要的是一个数组，可以引入多个配置类。

      * @Import注解在配置类中只能写一次，下面的方式是 **不允许的**

         .. code-block:: java

            @Configuration
            //@ComponentScan("com.itheima.config")
            @Import(JdbcConfig.class)
            @Import(Xxx.class)
            public class SpringConfig {

            }

总结
--------------------------

.. figure:: images/4.jpg
   :figclass: align-center

