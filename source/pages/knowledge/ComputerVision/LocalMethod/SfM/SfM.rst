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

   incremental pipeline in colmap

该方法最早可以追溯到 [1]_ ，目前使用较多的方法 [2]_ [3]_ [4]_ [5]_ [6]_ [7]_ 也是以其为基础。

增量式重建对于特征匹配以及外极几何关系的外点比较鲁棒，重建场景精度高:

1.标定过程中通过RANSAC不断地过滤外点

2.捆绑调整（Bundle Adjustment, BA）不断地优化场景结构

.. [1] Seitz S M, Szeliski R, Snavely N. Photo Tourism: Exploring Photo Collections in 3D[J]. Acm Transactions on Graphics, 2006, 25(3):835-846.

.. [2] Agarwal S, Snavely N, Simon I, et al. Building Rome in a day[J]. Communications of the Acm, 2011, 54(10):105-112.

.. [3] Snavely K N. Scene reconstruction and visualization from internet photo collections[M]. University of Washington, 2008.

.. [4] Frahm J M, Fite-Georgel P, Gallup D, et al. Building Rome on a cloudless day[C] European Conference on Computer Vision. Springer-Verlag, 2010:368-381.

.. [5] Wu C. Towards Linear-Time Incremental Structure from Motion[C] International Conference on 3dtv-Conference. IEEE, 2013:127-134.

.. [6] Moulon P, Monasse P, Marlet R. Adaptive structure from motion with a contrario, model estimation[C] Asian Conference on Computer Vision. Springer Berlin Heidelberg, 2012:257-270.

.. [7] Schönberger J L, Frahm J M. Structure-from-Motion Revisited[C] Computer Vision and Pattern Recognition. IEEE, 2016.


