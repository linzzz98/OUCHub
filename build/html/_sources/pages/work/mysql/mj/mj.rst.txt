Sql面经
=====================


1. SQL防注入
--------------------

所谓SQL注入，就是通过把SQL命令插入到Web表单提交或输入域名或页面请求的查询字符串，最终达到欺骗服务器执行恶意的SQL命令。

::
   比如在一个登录界面，要求输入用户名和密码：

   可以这样输入实现免帐号登录：

   用户名： ‘or 1 = 1 --

   密 码：

   .. note::

      SQL语句变成：

      SELECT * FROM user_table WHERE username=

      '’or 1 = 1 -- and password='’

      分析SQL语句：

      条件后面username=”or 1=1 用户名等于 ” 或1=1 那么这个条件一定会成功；

      然后后面加两个-，这意味着注释，它将后面的语句注释，让他们不起作用，这样语句永远都能正确执行，用户轻易骗过系统，获取合法身份。


**应对方法**

1. JDBC使用PreparedStatement

   PreparedStatement是预编译的,对于批量处理可以大大提高效率. 也叫JDBC存储过程

   * 创建PreparedStatement

      .. code-block:: java

            /** 1. init PreparedStatement*/
            Class.forName("com.mysql.jdbc.Driver");
            String url = "jdbc:mysql://localhost:3306/db_test?useSSL=false";
            String username = "root";
            String password = "root";

            Connection connection = DriverManager.getConnection(url, username, password);

            String sql = "update user set username=? where id = ?";

            PreparedStatement preparedStatement = connection.prepareStatement(sql);

   * 设置入参

      .. code-block:: java

         /** 2. prepare param*/
         preparedStatement.setString(1, "feifz");
         preparedStatement.setInt(2, 2);

   * 执行

      .. code-block:: java

         /** 3. execute update*/
         int result = preparedStatement.executeUpdate();
         System.out.printf("更新记录数："+result+"\n");

   * 执行查询

      如果是执行查询数据库的话，也像Statement对象执行excuteQuery()一样返回一个ResultSet结果集。

      .. code-block:: java

         /** 4. execute select*/
         String sql2 = "select * from user";
         ResultSet resultSet = preparedStatement.executeQuery(sql2);
         while (resultSet.next()) {
            int id = resultSet.getInt("id");
            String username = resultSet.getString("username");
            String dept = resultSet.getString("dept");
            System.out.println("id:"+id +"username->"+ username + ",dept-> " + dept );
         }



