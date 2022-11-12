Properties文件
====================================

1. 准备properties配置文件

   resources下创建一个jdbc.properties文件,并添加对应的属性键值对

   .. code:: xml

      jdbc.driver=com.mysql.cj.jdbc.Driver
      jdbc.url=jdbc:mysql://127.0.0.1:3306/test
      jdbc.username=root
      jdbc.password=123456

2. 开启context命名空间

   在applicationContext.xml中开 **context** 命名空间

   .. code:: xml

      .. figure:: images/1.jpg
         :figclass: align-center

      <?xml version="1.0" encoding="UTF-8"?>
      <beans xmlns="http://www.springframework.org/schema/beans"
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             xmlns:context="http://www.springframework.org/schema/context"
             xsi:schemaLocation="
                  http://www.springframework.org/schema/beans
                  http://www.springframework.org/schema/beans/spring-beans.xsd
                  http://www.springframework.org/schema/context
                  http://www.springframework.org/schema/context/spring-context.xsd">
      </beans>

3. 加载properties配置文件

   在配置文件中使用 ``context`` 命名空间下的标签来加载properties配置文件

4. 完成属性注入

   使用 ``${key}`` 来读取properties配置文件中的内容并完成属性注入

   .. code:: xml

       <context:property-placeholder location="jdbc.properties"/>

       <bean id="dataSource" class="com.alibaba.druid.pool.DruidDataSource">
           <property name="driverClassName" value="${jdbc.driver}"/>
           <property name="url" value="${jdbc.url}"/>
           <property name="username" value="${jdbc.username}"/>
           <property name="password" value="${jdbc.password}"/>
       </bean>

.. attention::

   1. 键值对的key为系统变量引发的问题

      ``<context:property-placeholder/>`` 标签会加载系统的环境变量，而且环境变量的值会被优先加载

      将system-properties-mode:设置为NEVER,表示不加载系统属性，就可以解决上述问题

      .. code:: xml

         <context:property-placeholder location="jdbc.properties" system-properties-mode="NEVER"/>

   2. 当有多个properties配置文件需要被加载，该如何配置?

      .. code:: xml

         <!--方式一 -->
         <context:property-placeholder location="jdbc.properties,jdbc2.properties" system-properties-mode="NEVER"/>
         <!--方式二-->
         <context:property-placeholder location="*.properties" system-properties-mode="NEVER"/>
         <!--方式三 -->
         <context:property-placeholder location="classpath:*.properties" system-properties-mode="NEVER"/>
         <!--方式四-->
         <context:property-placeholder location="classpath*:*.properties" system-properties-mode="NEVER"/>

      **说明:**

         * 方式一: 可以实现，如果配置文件多的话，每个都需要配置

         ..

         * 方式二: ``*.properties`` 代表所有以properties结尾的文件都会被加载，可以解决方式一的问题，但是不标准

         ..

         * 方式三: 标准的写法，``classpath:`` 代表的是从根路径下开始查找，但是只能查询当前项目的根路径

         ..

         * 方式四: 不仅可以加载当前项目还可以加载当前项目所依赖的所有项目的根路径下的properties配置文件