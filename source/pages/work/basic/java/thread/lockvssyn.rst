Lock 和 Synchronized 的区别
================================

语法层面
---------------

* synchronized是关键字，源码在jvm，用c++实现

* lock是接口，源码由jdk提供，用java实现

* 使用synchronized时，退出同步代码块锁会自动释放，而使用lock时需要手动调用unlock方法释放锁

功能层面
-----------------

* 两者均属于悲观锁，都具备基本的互斥、同步、锁重入功能

* Lock提供了许多synchronized不具备的功能，例如获取等待状态，公平锁，可打断，可超时等

* Lock有适合不同场景的实现，入 ReentrantLock，ReentrantReadWriteLock

性能层面
-----------------

* 没有竞争时，synchronized做了很多优化，如偏向锁，轻量级锁

* 在竞争激烈时，Lock的实现通常会提供更好的性能