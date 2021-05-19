Structure from Motion
======================

SfM（运动恢复结构）是一个通过输入无序（有序）的图片恢复所有相机位姿和生成稀疏点云的过程。

SfM大致可以分为以下四个类型

1. Incremental SfM

2. Global SfM

3. Hybrid SfM

4. DeepLearning Method

Incremental SfM
----------------

.. figure:: incremental_1.jpg
   :figclass: align-center

该方法最早可以追溯到 [1]_

对于特征匹配以及外极几何关系的外点比较鲁棒，重建场景精度高:

1.标定过程中通过RANSAC不断地过滤外点

2.捆绑调整（Bundle Adjustment, BA）不断地优化场景结构

.. _[1]: Seitz S M, Szeliski R, Snavely N. Photo Tourism: Exploring Photo Collections in 3D[J]. Acm Transactions on Graphics, 2006, 25(3):835-846.


