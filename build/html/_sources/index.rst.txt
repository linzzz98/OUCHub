.. colmap documentation master file, created by
   sphinx-quickstart on Thu Mar  4 16:10:53 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

欢迎来到linzzz的学习库!
==================================

.. figure:: images/index/cat.jpg
    :figclass: align-center

    占位符

About
-----

OUC_B419_Linzzz代码论文仓库。

.. attention::
   git add .

   git commit -m "更新备注"

   git push origin master
.. caution::
   https://ouchub.readthedocs.io
.. danger::

   .. figure:: images/font.jpg
    :figclass: align-center

.. hint::

   :用语解释:

      在局部参考系中表示的一组摄影机和3D点(具有两个摄影机的stereo-models）称为\ **Model**\ 。

      从多个图像中的对应点计算3D点坐标的过程称为\ **intersection**\ (也称为\ **triangulation**\ ）。

      从已知的3D-2D对应关系恢复相机矩阵(完全或仅限于外部参数）称为\ **resection**\ 。

      从两个图像中的对应点检索两个摄像机的相对位置和姿态的任务称为\ **relative
      orientation**\ 。

      计算将两个共享一些tie-points的模型带到一个公共参考系中的刚性(或相似性）变换的任务称为\ **absolute
      orientation**\ 。

.. error::
   1
.. important::

   **顶级期刊**
      * PAMI, IEEE Transactions on Pattern Analysis and Machine Intelligence
      * IJCV, International Journal of Computer Vision

   **顶级会议**
      * ICCV, IEEE International Conference on Computer Vision（两年一次）
      * CVPR,IEEE Conference on Computer Vision and Pattern Recognition（一年一次）
      * ECCV,European Conference on Computer Vision（两年一次）

.. tip::
   1
.. note::
   :ref:`genindex`


.. .. highlight:: c++

.. toctree::
   :maxdepth: -1
   :hidden:
   :caption: 基础知识

   pages/knowledge/k_MH
   pages/knowledge/k_CV
   pages/knowledge/k_ML

.. toctree::
   :maxdepth: -1
   :hidden:
   :caption: 论文学习

   pages/paper/p_sfm
   pages/paper/p_pointcloud
   pages/paper/p_others

.. toctree::
   :maxdepth: -1
   :hidden:
   :caption: 源码解析

   pages/code/colmap
   pages/code/theiasfm


.. toctree::
   :maxdepth: -1
   :hidden:
   :caption: 杂七杂八

   pages/others/o_others
