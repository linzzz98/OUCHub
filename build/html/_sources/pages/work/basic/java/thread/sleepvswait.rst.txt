Sleep 和 Wait 的区别
================================

* 共同点： wait()，wait(long) 和 sleep(long) 的效果都是让当前线程暂时放弃CPU的使用权，进入阻塞状态

* 方法归属不同：

   1. sleep(long) 是 Thread 的静态方法
   2. wait()，wait(long)，都是Object的成员方法，每个对象都有

*  醒来时机不同

   1. 执行sleep(long) 和 wait(long) 的线程都会在等待响应毫秒后醒来
   2. wait(long) 和 wait() 还可以被 notify 唤醒， wait() 如果不唤醒就需要一直等下去。
   3. 都可以被打断唤醒

* 锁特性不同

   1. wait方法的调用必须线获取wait对象的锁，而sleep无此限制
   2. wait方法执行后释放对象锁，允许其他线程获得该对象锁
   3. sleep如果在 synchronized 代码中执行，并不会释放对象锁。