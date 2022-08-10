单例模式
=============================

实现
-----------------------------

懒汉式
^^^^^^^^^^^^^^^^^^^^

.. code-block:: java

   public class SingleInstance implements Serializable {

       private SingleInstance(){

       }

       private static SingleInstance2 instance = new SingleInstance2();

       public static SingleInstance2 getInstance(){
           return instance;
       }

   }

破环单例
^^^^^^^^^^^^^^^^^^^^^^

1. 反射破坏单例

.. code-block:: java

    private static void reflection(Class<?> clazz) throws Exception{
        Constructor<?> constructor = clazz.getDeclaredConstructor();
        constructor.setAccessible(true);
        System.out.println("反射创建实例：" + constructor.newInstance());
    }

**预防**

修改单例的构造函数，如果已经创建，则抛出异常

.. code-block:: java

   private SingleInstance(){
      if(instance != null){
         throw new RuntimeException("单例已经存在");
      }
   }

2. 序列化破坏单例

.. code-block:: java

    private static void serializable(Object instance) throws Exception{
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        ObjectOutputStream oos = new ObjectOutputStream(bos);
        oos.writeObject(instance);
        ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(bos.toByteArray()));
        System.out.println("反序列化创建实例:" + ois.readObject());
    }

**预防**

在单例类中重写 ``readResolve`` 方法

.. code-block:: java

    @Serial
    public Object readResolve(){
        return instance;
    }

3. Unsafe破坏单例

.. code-block:: java

    private static void unsafe(Class<?> clazz) throws Exception{
        Object o = UnsafeUtils.getUnsafe().allocateInstance(clazz);
        System.out.println("Unsafe 创建实例:" + o);
    }

**无法预防**