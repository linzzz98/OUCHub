PnP
======

.. toctree::
   :maxdepth: -1
   :hidden:

   P3P/P3P
   EPnP/EPnP

* :doc:`P3P <P3P/P3P>`
* :doc:`EPnP <EPnP/EPnP>`

**成员变量**

1. 2D图像特征观察值

.. cpp:type:: Eigen::Vector2d X_t

2. 世界框架中观察到的3D特征

.. cpp:type:: Eigen::Vector3d Y_t

3. 从世界到相机框架的转变

.. cpp:type:: Eigen::Matrix3x4d M_t

4. 估计模型所需的最少样本数

.. cpp:member:: static const int kMinNumSamples
