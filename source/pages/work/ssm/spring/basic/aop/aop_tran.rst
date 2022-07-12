AOP事务管理
=============================

Spring事务简介
-----------------------------

Spring为了管理事务，提供了一个平台事务管理器 ``PlatformTransactionManager``

.. figure:: images/11.jpg
   :figclass: align-center

``commit`` 是用来提交事务，``rollback`` 是用来回滚事务。

PlatformTransactionManager只是一个接口，Spring还为其提供了一个具体的实现:

.. figure:: images/12.jpg
   :figclass: align-center

案例
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

需求: 实现任意两个账户间转账操作

需求微缩: A账户减钱，B账户加钱

为了实现上述的业务需求，按照下面步骤来实现下:

①：数据层提供基础操作，指定账户减钱（outMoney），指定账户加钱（inMoney）

②：业务层提供转账操作（transfer），调用减钱与加钱的操作

③：提供2个账号和操作金额执行转账操作

④：基于Spring整合MyBatis环境搭建上述操作

