DeepSFM: Structure From Motion Via Deep Bundle Adjustment
=========================================================

早期的努力将深度神经网络用作强大的映射功能，可以直接回归结构和运动（regresses the structures and motions）。
由于没有明确强制执行结构和运动的几何约束，因此网络无法学习基本的物理原理，因此容易出现过拟合现象。 因此，它们的性能不如传统的SfM方法，并且泛化能力极差。

最近的研究引入了3D cost volume，以可区分的方式显式地利用照片一致性，从而显着提高基于深度学习的3D重建的性能。

本文受BA和深度估计 cost volume 的启发，为SfM提出了一个深度学习框架，该框架根据明确建立用于测量照片一致性和几何一致性的成本量来迭代地改善深度和相机姿态。
该方法不需要精确的位姿（粗略的估计就足够）。 特别的，网络包括基于深度的cost volume（D-CV）和基于位姿的cost volume（P-CV）。

D-CV使用当前相机位姿优化每个像素的深度值，而P-CV使用当前深度估算值优化照相机的位姿。

.. figure:: 1.jpg
   :figclass: align-center

.. hint::

   DeepSFM会根据附近的一些原始图像来优化目标图像的深度和相机位姿。 该网络包括基于深度的cost volume（D-CV）和基于位姿的cost volume（P-CV），将图像一致性和几何一致性强制为3D cost volume， 整个过程迭代执行。


常规的3D cost volume 通过将像素不投影到离散的相机的正面和平行平面中并计算光度（即图像特征）差异作为cost来增强照片一致性。注意，可以使用常规3D cost volume获得初始深度估计。


