Using Many Cameras as One
============================

:贡献:

   1.提出"广义相机模型"框架，表达了一个多相机系统。

   2.从该模型的运动约束方程推导出结构。来自运动约束的微分结构给出了一个误差函数，该函数定义了运动估计的最小化问题。

   3. 考虑到该误差函数的 Fisher 信息矩阵，可以根据估计自我运动的能力对不同相机设计进行定量比较。

广义相机模型被引入作为统一分析和描述广泛不同的新相机设计集的工具。该模型从光通过任意成像系统的透镜和反射镜时所采用的路径中抽象出来。它用影响该传感器的空间区域来识别每个像素。 这个空间区域的合理模型是从某个点发出的圆锥体。

.. figure:: 1.jpg
   :figclass: align-center

.. note::

   成像模型的完整定义是根据“raxels”定义的。（上图） 由广义相机拍摄的图像被定义为系统捕获的一组raxels测量值。

   raxel 定义了像素如何对场景进行采样。假设该采样以从  :math:`X、Y、Z` 点开始的射线为中心，方向由 :math:`(φ, θ)` 参数化。 该像素从围绕该射线的锥体捕获光，其纵横比和方向由  :math:`(f_a , f_b , \gamma)` 给出。 捕获的光强度也可能会衰减，这些辐射量可能因每个像素而异。

对于多幅图像的几何分析，简化了这种校准，使其仅包括像素采样的光线的定义。

|:point_right:| 这给出了一个更简单的校准问题，它需要为每个像素确定采样线的 Plucker 矢量。

Plucker Vectors
-----------------

为了描述在这个更一般的相机设置中每个像素采样的空间线，需要一种机制来描述空间中的任意线。

一条线的 Plucker 向量是一对3维向量： :math:`q,q'` ，命名为方向向量（direction vector）和力矩向量（moment vector）。

.. note::

   :math:`q`  是线方向上任意长度的向量。

   对于直线上的任意点 :math:`P` ， :math:`q' = q \times P` 。

这对向量必须满足两个约束条件。

1.  :math:`q · q' = 0`

2. 其余五个参数是齐次的，它们的整体尺度不影响它们描述的是哪条线。

.. note::

   将方向向量强制为单位向量通常很方便，它定义了齐次参数的尺度。

与这些 Plucker 向量位于一条直线上的所有点的集合由下式给出：

.. math::

   (q \times q') + \alpha q, \forall \alpha \in R

.. attention::

   如果 :math:`q` 是单位向量，则点  :math:`(q\times q')` 是直线上最接近原点的点， :math:`\alpha` 是该点到原点（？原点到该点？ distance from that point.）的（有符号）距离。

Plucker Vectors of a Multi-Camera System
------------------------------------------

