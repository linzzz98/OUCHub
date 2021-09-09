Privacy Preserving Structure-from-Motion
=========================================

|:point_right:| \ `原文链接 <https://cvg.ethz.ch/research/privacy-preserving-sfm/paper/Geppert2020ECCV.pdf>`_
|:point_right:| \ `源码 <https://github.com/colmap/privacy_preserving_sfm>`_


背景：最近基于云的定位和地图系统的趋势引起了严重的隐私问题。即使只上传了派生的图像特征，也可能会泄露潜在的机密信息。

本文建立在将 2D/3D 特征点提升到随机线，同时仍然提供相机姿态估计的充分约束的基础上，针对基于随机线特征的增量SfM管道的不同核心算法提出解决方案。

.. note::

   本文的贡献

   1. 基于colmap提出了基于线特征的端到端的隐私保密SfM pipeline

   2. 对于增量SfM的每个阶段（初始化、后方交会、三角测量、BA）都在隐私保护设置中提出了相应的措施。

   3. 推导出一个最小求解器从四个视图初始化增量SfM pipeline

Initialization
---------------

仅从相应的 2D 线特征无法从两个视图执行初始化。

注意：两条反向投影的 2D 线成为 3D 平面，并且无论相机如何摆位姿，都将始终在 3D 线中相交，因此线-线对应关系对两视图的相对位姿没有限制。

第一个约束出现在四个视图中。 四幅图像的相对姿态由四焦张量描述。

.. attention::

   虽然理论上可以从线对应估计四焦张量，但由于四焦张量的内部约束的高度复杂性，目前没有易于处理的方法。

本文提出了一种从基于线的对应关系执行鲁棒初始化的替代方法。

.. important::

   该方法基于知道用于初始化的图像的重力方向的假设，这是合理的，因为现在几乎所有设备都带有惯性测量单元。

   此外，利用了这样一个事实，即可以控制创建随机线的过程。

   核心思想是将线特征的随机子集与重力方向对齐。这些线现在始终面向世界框架。

如果相机姿势正确，则背投影线的平面现在应该与（面向重力的）3D 线相交。这对相对位姿产生了额外的约束，可以用它来简化估计问题的复杂性。

重力对齐的特征线允许分解初始化问题，这样首先解决二维 SfM 问题，然后将相机升级为三维。

假设相机已经旋转，使得 y 轴与已知的重力方向重合。一旦相机的坐标系 **gravity-aligned** ，每个相机只剩下四个自由度：围绕 y 轴的旋转 :math:`\theta` 和平移分量 :math:`(tx,ty,tz)^T` 。

考虑由通过二维点  :math:`(x, y)`  的垂直线  :math:`\mathcal{l} = (−1, 0, x)`  构成的约束：

.. math::

   (-1,0,x)\left(
   \begin{matrix}
   \left[
   \begin{matrix}
   cos\theta & 0 & sin\theta\\
   0 & 1 & 0\\
   -sin\theta & 0 & cos\theta
   \end{matrix}
   \right]\left(
   \begin{matrix}
   X\\Y\\Z
   \end{matrix}
   \right)+\left(
   \begin{matrix}
   t_x\\t_y\\t_z
   \end{matrix}
   \right)
   \end{matrix}
   \right) = 0

请注意，重力对齐线不会对 :math:`Y` 或 :math:`t_y` 施加任何约束。 这是因为它们仅沿重力方向平移 3D 点 X、Y、Z 或相机，因此可将上式改为：

.. math::

   (-1,x)\left(
   \begin{matrix}
   \left[
   \begin{matrix}
   cos\theta & 0 & sin\theta\\
   -sin\theta & 0 & cos\theta
   \end{matrix}
   \right]\left(
   \begin{matrix}
   X\\Z
   \end{matrix}
   \right)+\left(
   \begin{matrix}
   t_x\\t_z
   \end{matrix}
   \right)
   \end{matrix}
   \right) = 0

这个方程正是 2D 到 1D 相机的投影方程，例如：

.. math::

   \lambda \left(
   \begin{matrix}
   x\\1
   \end{matrix}
   \right) = R_{2\times 2} \left(
   \begin{matrix}
   X\\Z
   \end{matrix}
   \right) + t_{2\times 1}

可以将问题分解为首先使用重力对齐的对应关系解决 2D 相对姿势问题。

该问题的解产生完整的相机方向 :math:`\theta` 以及与重力正交的两个平移分量 :math:`t_x,t_z` 。 唯一剩下的未知数是重力对齐的平移 :math:`t_y` ，它无法从重力对齐的线中观察到。

为了恢复这些，需要使用在图像中随机定向的额外线对应。

二维三焦张量是一个 :math:`2 × 2 × 2` 张量，它约束一维图像测量 :math:`x_i \in P_1, i = 1, 2, 3`  为：

.. math::

   [x_1^T T_1 x_2, x_1^T T_2 x_2] x_3 = 0

其中 :math:`T_1` 和 :math:`T_2` 是张量的 :math:`2 × 2` 切片。