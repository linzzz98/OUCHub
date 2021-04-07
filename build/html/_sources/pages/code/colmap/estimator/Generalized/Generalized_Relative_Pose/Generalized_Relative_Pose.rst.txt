Generalized_RelativePose
==============================

使用最少8个2D-2D对应关系求解广义相对姿势问题。

.. parsed-literal::

    \ `Efficient Computation of Relative Pose for Multi-Camera Systems <https://openaccess.thecvf.com/content_cvpr_2014/papers/Kneip_Efficient_Computation_of_2014_CVPR_paper.pdf>`_

.. cpp:class:: GR6PEstimator

成员变量
-------------------

.. cpp:struct:: GR6PEstimator::X_t

   左摄像机的广义图像观察，它由广义摄像机中特定摄像机的相对姿势及其图像观察值组成

:X_t:

   .. cpp:member:: Eigen::Matrix3x4d GR6PEstimator::rel_tform;

      从广义摄像机到观测摄像机的框架的相对转换

   .. cpp:member:: Eigen::Vector2d GR6PEstimator::xy;

      2D图像特征观察值

.. cpp:type:: X_t GR6PEstimator::Y_t;

   左图像的归一化图像特征点

.. cpp:type:: Eigen::Matrix3x4d GR6PEstimator::M_t;

   两个广义相机之间的相对转换

.. cpp:member:: static const int GR6PEstimator::kMinNumSamples = 8;

   估计模型所需的最少样本数

   .. attention::

      请注意，理论上最少需要的样本数量为6，但是Laurent Kneip在他的论文中表明，使用8个样本更为稳定。

成员函数
---------------------------

Estimate
~~~~~~~~~
