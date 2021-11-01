Geometric Interpretations of the Normalized Epipolar Error
==========================================================

本文提供了归一化对极误差的几何解释。

表明它与以下量直接相关：

（1）两条反向投影光线之间的最短距离

..

（2）两个边界对极平面之间的二面角

..

（3）L1 - 最优角度重投影误差。


考虑两个相机 :math:`c_0` 和 :math:`c_1` 观察相同的 3D 点 :math:`p` 。

如果已知两台相机的内参和相对位姿，就可以对每幅图像中的测量点进行反投影，得到每台相机发出的指向 :math:`p` 的光线。

定义归一化对极误差如下：

.. math::

   \hat{e} := |\hat{f}_1 · (\hat{t} \times R\hat{f}_0)| = |\hat{f} · (R \hat{f}_0 \times \hat{f}_1)|

其中 :math:`f_0` 和 :math:`f_1` 是来自 :math:`c_0` 和 :math:`c_1` 的反向投影单位光线，
:math:`R` 是旋转矩阵， :math:`t` 是将一个点从参考系 :math:`c_0` 变换到 :math:`c_1` 的平移向量： :math:`x_1 = Rx_0 + t` 以及 :math:`\hat{t} = t / ||t||`

.. note::

   上面公式中的第二个等式源于以下事实：标量三重积对于循环移位是不变的。

   The scalar triple product is invariant to a circular shift.

在文献中，误差 :math:`e` 常表示如下：

.. math::

   \hat{e} = |\hat{f}_1^T E \hat{f}_0|

其中  :math:`E = [\hat{t}]_\times R`  是基本矩阵，  :math:`[·]_{\times}`  是偏对称算子。

如果图像测量、标定和位姿数据都非常准确，则该误差将为零，因为 :math:`R \hat{f}_0 , \hat{f}_1` 和 :math:`t` 将共面。

.. figure:: 1.jpg
   :figclass: align-center

这称为对极约束。

在文献中，归一化对极误差大多被视为没有几何意义的代数量，这种误解源于这样一个事实，即“标准”对极误差 :math:`e` 是一个代数量。

其中 :math:`f_0` 和 :math:`f_1` 分别是 :math:`c_0` 和 :math:`c_1` 中点的归一化图像坐标。

.. attention::

   请注意，(1) 和 (3) 之间的唯一区别是光线归一化的方式：

   在 (1) 中，它们按长度归一化。

   在 (3) 中，它们由向量中的最后一个元素归一化。

Geometric Interpretations
-------------------------

.. figure:: 2.jpg
   :figclass: align-center

