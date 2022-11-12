Maven
========================

分模块开发
------------------------

将原始模块按照功能拆分成若干个子模块，方便模块间的相互调用，接口共享。

.. figure:: images/1.jpg
   :figclass: align-center

建立依赖关系
~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: xml

   <dependency>
       <groupId>com.linzzz</groupId>
       <artifactId>maven_03_pojo</artifactId>
       <version>1.0-SNAPSHOT</version>
   </dependency>

将项目安装本地仓库
~~~~~~~~~~~~~~~~~~~~~~~~

将需要被依赖的项目 **maven_03_pojo** ，使用maven的install命令，把其安装到Maven的本地仓库中。

.. figure:: images/2.jpg
   :figclass: align-center

安装成功后，在对应的路径下就看到安装好的jar包

.. figure:: images/3.jpg
   :figclass: align-center

.. note::

   **说明:** 具体安装在哪里，和电脑上Maven的本地仓库配置的位置有关。

总结
~~~~~~~~~~~~~~~~~~~~~~~~~~

对于项目的拆分，大致会有如下几个步骤:

(1) 创建Maven模块

(2) 书写模块代码

   分模块开发需要先针对模块功能进行设计，再进行编码。不会先将工程开发完毕，然后进行拆分。拆分方式可以按照功能拆也可以按照模块拆。

(3)通过maven指令安装模块到本地仓库(install 指令)

依赖管理
----------------------------

``<dependency>`` 被称为依赖，依赖管理里面涉及以下内容:

* 依赖传递
* 可选依赖
* 排除依赖

依赖指当前项目运行所需的jar，一个项目可以设置多个依赖。

.. code:: xml

   <!--设置当前项目所依赖的所有jar-->
   <dependencies>
       <!--设置具体的依赖-->
       <dependency>
           <!--依赖所属群组id-->
           <groupId>org.springframework</groupId>
           <!--依赖所属项目id-->
           <artifactId>spring-webmvc</artifactId>
           <!--依赖版本号-->
           <version>5.2.10.RELEASE</version>
       </dependency>
   </dependencies>

**依赖传递与冲突问题**

.. figure:: images/4.jpg
   :figclass: align-center

在项目所依赖的这些jar包中，有一个比较大的区别就是**有的依赖前面有箭头>,有的依赖前面没有。**

打开前面的箭头，发现这个jar包下面还包含有其他的jar包

.. figure:: images/5.jpg
   :figclass: align-center

依赖传递
~~~~~~~~~~~~~~~~~~~~~~

.. figure:: images/6.jpg
   :figclass: align-center

**说明:**

   A代表自己的项目；B,C,D,E,F,G代表的是项目所依赖的jar包；D1和D2 E1和E2代表是相同jar包的不同版本

   (1) A依赖了B和C,B和C有分别依赖了其他jar包，所以在A项目中就可以使用上面所有jar包，这就是所说的依赖传递

   (2) 依赖传递有直接依赖和间接依赖

   * 相对于A来说，A直接依赖B和C,间接依赖了D1,E1,G，F,D2和E2
   * 相对于B来说，B直接依赖了D1和E1,间接依赖了G
   * 直接依赖和间接依赖是一个相对的概念

   (3)因为有依赖传递的存在，就会导致jar包在依赖的过程中出现冲突问题

特殊优先
^^^^^^^^^^^^^^^^^

添加两个不同版本的Junit依赖:

.. code:: xml

   <dependencies>
       <dependency>
         <groupId>junit</groupId>
         <artifactId>junit</artifactId>
         <version>4.12</version>
         <scope>test</scope>
       </dependency>

       <dependency>
         <groupId>junit</groupId>
         <artifactId>junit</artifactId>
         <version>4.11</version>
         <scope>test</scope>
       </dependency>
   </dependencies>


**特殊优先：当同级配置了相同资源的不同版本，后配置的覆盖先配置的。**

路径优先
^^^^^^^^^^^^^^^^^^^^^^^

当依赖中出现相同的资源时，层级越深，优先级越低，层级越浅，优先级越高

* A通过B间接依赖到E1
* A通过C间接依赖到E2
* A就会间接依赖到E1和E2,Maven会按照层级来选择，E1是2度，E2是3度，所以最终会选择E1

声明优先
^^^^^^^^^^^^^^^^^^^^^^^

当资源在相同层级被依赖时，配置顺序靠前的覆盖配置顺序靠后的

* A通过B间接依赖到D1
* A通过C间接依赖到D2
* D1和D2都是两度，这个时候就不能按照层级来选择，需要按照声明来，谁先声明用谁，也就是说B在C之前声明，这个时候使用的是D1，反之则为D2
