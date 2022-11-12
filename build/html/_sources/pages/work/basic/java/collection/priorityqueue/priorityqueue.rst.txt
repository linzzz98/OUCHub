PriorityQueue
=======================

Java PriorityQueue 实现了 Queue 接口，不允许放入 null 元素；其通过堆实现，具体说是

通过完全二叉树（complete binary tree）实现的小顶堆（任意一个非叶子节点的权值，都不

大于其左右子节点的权值），也就意味着可以通过数组来作为PriorityQueue 的底层实现，

数组初始大小为11；也可以用一棵完全二叉树表示。

**优先队列的作用是能保证每次取出的元素都是队列中权值最小的**

构造方法
----------------------

.. code-block:: java

   // JDK下的优先级队列是基于最小堆实现的
   Queue<Integer> queue1 = new PriorityQueue<>();
   // 元素操作
   queue1.offer(1); // 入队
   queue1.poll(); // 出队
   queue1.peek(); // 返回队首元素(最小值)

   // 改造：如果想使用基于最大堆的优先级队列可以这样改
   Queue<Integer> queue2 = new PriorityQueue<>(new Comparator<Integer>() {
       @Override
       public int compare(Integer o1, Integer o2) {
           return o2 - o1;
       }
   });

   // 改造2：对于类型为自定义类的优先级队列可以这样改
   PriorityQueue<ListNode> queue3 = new PriorityQueue<>(
           lists.length, (a, b)->(a.val - b.val));

常用方法总结
------------------------

public boolean add(E e); //在队尾插入元素，插入失败时抛出异常，并调整堆结构

public boolean offer(E e); //在队尾插入元素，插入失败时抛出false，并调整堆结构

public E remove(); //获取队头元素并删除，并返回，失败时前者抛出异常，再调整堆结构

public E poll(); //获取队头元素并删除，并返回，失败时前者抛出null，再调整堆结构

public E element(); //返回队头元素（不删除），失败时前者抛出异常

public E peek()；//返回队头元素（不删除），失败时前者抛出null

public boolean isEmpty(); //判断队列是否为空

public int size(); //获取队列中元素个数

public void clear(); //清空队列

public boolean contains(Object o); //判断队列中是否包含指定元素（从队头到队尾遍历）

public Iterator<E> iterator(); //迭代器

堆结构调整
----------------------

每次插入或删除元素后，都对队列进行调整，使得队列始终构成最小堆（或最大堆）。

具体调整如下：

   * 插入元素后，从堆底到堆顶调整堆；

   * 删除元素后，将队尾元素复制到队头，并从堆顶到堆底调整堆。

应用(topK问题)
-------------------------

**topK问题是指：从海量数据中寻找最大的前k个数据，比如从1亿个数据中，寻找最大的1万个数。**

.. note::

   最小或最大的k个元素 =》都是优先级队列 (堆的应用)
      * 找最小的k个数，就构造最大堆。
      * 找最大的k个数，就构造最小堆。

   原因：
      * 当你需要找k个较小的数时，你的最大堆顶部一定是堆中最大的元素。当遍历完所有元素时，堆顶的元素相比其它元素已经算是较小的元素了，那么堆中的其它元素一定更小。这样就有效地筛选出k个小值了。


e.g.

例1： 给定整数数组 nums 和整数 k，请返回数组中 k 个最小的元素。你需要找的是数组排序后的第 k 个最大的元素，而不是第 k 个不同的元素。

      例如，输入4、5、1、6、2、7、3、8这8个数字，则最小的4个数字是1、2、3、4。

.. code-block:: java

    public int[] getLeastNumbers(int[] arr, int k) {
        if(k == 0){
            return new int[0];
        }

        // 使用一个最大堆（大顶堆）
        // Java 的 PriorityQueue 默认是小顶堆，添加 comparator 参数使其变成最大堆
        // 不能使用 b - a !!!
        Queue<Integer> heap = new PriorityQueue<>(k, (a, b) -> Integer.compare(b, a));

        for(int e : arr){
            // 当前数字小于堆顶元素才会入堆
            if(heap.isEmpty() || heap.size() < k || e < heap.peek()){
                heap.offer(e);
            }
            if(heap.size() > k){
                heap.poll(); // 删除堆顶最大元素
            }
        }

        int[] res = new int[k];
        int j = 0;
        for (int e : heap) { res[j++] = e; }
        return res;
    }


总结
-----------------------

1、jdk内置的优先队列PriorityQueue内部使用一个堆维护数据，每当有数据add进来或者poll出去的时候会对堆做从下往上的调整和从上往下的调整。

2、PriorityQueue不是一个线程安全的类，如果要在多线程环境下使用，可以使用 PriorityBlockingQueue 这个优先阻塞队列。其中add、poll、remove方法都使用 ReentrantLock 锁来保持同步，take() 方法中如果元素为空，则会一直保持阻塞。