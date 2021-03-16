.. default-domain:: cpp
.. default-domain:: cpp

EPnP
=====

EPNP求解器，用于解决PNP(透视N点)问题。 求解器至少需要4个2D-3D对应关系。

.. parsed-literal::

    \ `Epnp: An accurate o (n) solution to the pnp problem <http://www.iri.upc.edu/people/fmoreno/Publications/2009/pdf/Lepetit_ijcv2009.pdf>`_

论文解读
~~~~~~~~~~~~

.. attention::

   本章参考自 |:point_right:|    `《深入EPnP算法》 <https://blog.csdn.net/jessecw79/article/details/82945918>`_

在论文中，采用上标 :math:`^w` 和 :math:`^c` 表示在世界坐标系和摄像头坐标系中的坐标。那么：

:3D参考点:

* 在世界坐标系中的坐标为 :math:`p_i^w, ~~~i = 1,...,n`

* 在相机参考坐标系中的坐标为 :math:`p_i^c, ~~~i = 1,...,n`

:4个控制点:

* 在世界坐标系的坐标为 :math:`c_j^w, ~~~j = 1,...,4`

* 在相机参考坐标系中的坐标为 :math:`p_j^c, ~~~j = 1,...,4`

.. important::
   在EPnP论文中，以上坐标均为非齐次坐标。

EPnP算法将参考点的坐标表示为控制点坐标的加权和：

   .. math::

      p_i^w = \sum\limits_{j=1}^4 \alpha_{ij}c_j^w, ~~~ with \sum\limits_{j=1}^4 \alpha_{ij} = 1

其中 :math:`\alpha_{ij}` 是 ``齐次的barycentric坐标``

一旦虚拟控制点确定后，且满足4个控制点不共面的前提， :math:`\alpha_{ij}` 唯一被确定。

在相机坐标系中存在同样的加权关系：

.. math::

   p_i^c = \sum\limits_{j=1}^4 \alpha_{ij}c_j^c

假设相机的外参为 :math:`[R, t]`， 那么虚拟控制点 :math:`c_j^w` 和 :math:`c_j^c` 之间存在关系：

.. math::

   c_j^c = [R~~~t]\left[
   \begin{matrix}
   c_j^w \\ 1
   \end{matrix}
   \right]

考虑到EPnP算法将参考点坐标表示为控制点坐标的加权和，可以得到：

.. math::

   p_i^c = [R~~~t] \left[
   \begin{matrix}
   c_j^w \\ 1
   \end{matrix}
   \right] = [R~~~t] \left[
   \begin{matrix}
   \sum\limits_{j=1}^4 \alpha_{ij}c_j^w \\ 1
   \end{matrix}
   \right]

进而 |:point_down:| ：

.. math::

   p_i^c = [R~~~t]\left[
   \begin{matrix}
   \sum\limits_{j=1}^4 \alpha_{ij}c_j^w \\ \sum\limits_{j=1}^4 \alpha_{ij}
   \end{matrix}
   \right] = \sum\limits_{j=1}^4 \alpha_{ij}[R~~~t]\left[
   \begin{matrix}
   c_j^w \\ 1
   \end{matrix}
   \right] = \sum\limits_{j=1}^4 \alpha_{ij}c_j^c

.. note::
   在上述推导过程中，用到了EPnP对权重 :math:`\alpha_{ij}` 的重要约束条件 :math:`\sum\limits_{j=1}^4 \alpha_{ij} = 1`

.. attention::
   为什么3个控制点不行呢？

   四个方程，三个未知数，是一个超定方程组。不存在精确满足方程的解。

.. important::

   当四个控制点堆叠在一起时：

   .. math::

      \left[
      \begin{matrix}
      p_i^w\\1
      \end{matrix}
      \right] = C \left[
      \begin{matrix}
      \alpha_{i1}\\ \alpha_{i2} \\ \alpha_{i3} \\ \alpha_{i4}
      \end{matrix}
      \right] = \left[
      \begin{matrix}
      c_1^w & c_2^w & c_3^w & c_4^w\\
      1 & 1 & 1 & 1
      \end{matrix}
      \right]\left[
      \begin{matrix}
      \alpha_{i1} \\ \alpha_{i2} \\ \alpha_{i3} \\ \alpha_{i4}
      \end{matrix}
      \right]

   |:star:| 也就论证了论文中之前提到的

   .. math::

      p_i^w = \sum\limits_{j=1}^4 \alpha_{ij}c_j^w, ~~~ with \sum\limits_{j=1}^4 \alpha_{ij} = 1

   本质上说明了3D参考的的齐次坐标是控制点齐次坐标的线性组合。


成员变量
~~~~~~~~~~~

1. 2D图像特征观察值

    :cpp:type:`X_t`

2. 世界框架中观察到的3D特征

    :cpp:type:`Y_t`

3. 从世界到相机框架的转变

    :cpp:type:`M_t`

4. 估计模型所需的最少样本数

    :cpp:member:`kMinNumSamples`


成员函数
~~~~~~~~~~~

1. **Estimate**

从一组三个2D-3D点对应关系中估计EPnP问题的最可能解决方案。

-  @param points2D Normalized 2D image points as 3x2 matrix.

-  @param points3D 3D world points as 3x3 matrix.

-  @return Most probable pose as length-1 vector of a 3x4 matrix.

.. cpp:function::   static std::vector<M_t> Estimate(const std::vector<X_t>& points2D, const std::vector<Y_t>& points3D);

.. code-block:: cpp

    std::vector<EPNPEstimator::M_t> EPNPEstimator::Estimate(
        const std::vector<X_t>& points2D, const std::vector<Y_t>& points3D) {
      CHECK_GE(points2D.size(), 4);
      CHECK_EQ(points2D.size(), points3D.size());

      EPNPEstimator epnp;
      M_t proj_matrix;
      if (!epnp.ComputePose(points2D, points3D, &proj_matrix)) {
        return std::vector<EPNPEstimator::M_t>({});
      }

      return std::vector<EPNPEstimator::M_t>({proj_matrix});
    }

2. **ComputePose**

.. cpp:function::   bool ComputePose(const std::vector<Eigen::Vector2d>& points2D, const std::vector<Eigen::Vector3d>& points3D, Eigen::Matrix3x4d* proj_matrix);

.. code-block:: cpp

    bool EPNPEstimator::ComputePose(const std::vector<Eigen::Vector2d>& points2D,
                                    const std::vector<Eigen::Vector3d>& points3D,
                                    Eigen::Matrix3x4d* proj_matrix) {
      points2D_ = &points2D;
      points3D_ = &points3D;

      ChooseControlPoints();

      if (!ComputeBarycentricCoordinates()) {
        return false;
      }

      const Eigen::Matrix<double, Eigen::Dynamic, 12> M = ComputeM();
      const Eigen::Matrix<double, 12, 12> MtM = M.transpose() * M;

      Eigen::JacobiSVD<Eigen::Matrix<double, 12, 12>> svd(
          MtM, Eigen::ComputeFullV | Eigen::ComputeFullU);
      const Eigen::Matrix<double, 12, 12> Ut = svd.matrixU().transpose();

      const Eigen::Matrix<double, 6, 10> L6x10 = ComputeL6x10(Ut);
      const Eigen::Matrix<double, 6, 1> rho = ComputeRho();

      Eigen::Vector4d betas[4];
      std::array<double, 4> reproj_errors;
      std::array<Eigen::Matrix3d, 4> Rs;
      std::array<Eigen::Vector3d, 4> ts;

      FindBetasApprox1(L6x10, rho, &betas[1]);
      RunGaussNewton(L6x10, rho, &betas[1]);
      reproj_errors[1] = ComputeRT(Ut, betas[1], &Rs[1], &ts[1]);

      FindBetasApprox2(L6x10, rho, &betas[2]);
      RunGaussNewton(L6x10, rho, &betas[2]);
      reproj_errors[2] = ComputeRT(Ut, betas[2], &Rs[2], &ts[2]);

      FindBetasApprox3(L6x10, rho, &betas[3]);
      RunGaussNewton(L6x10, rho, &betas[3]);
      reproj_errors[3] = ComputeRT(Ut, betas[3], &Rs[3], &ts[3]);

      int best_idx = 1;
      if (reproj_errors[2] < reproj_errors[1]) {
        best_idx = 2;
      }
      if (reproj_errors[3] < reproj_errors[best_idx]) {
        best_idx = 3;
      }

      proj_matrix->leftCols<3>() = Rs[best_idx];
      proj_matrix->rightCols<1>() = ts[best_idx];

      return true;
    }

3. **ChooseControlPoints**

.. cpp:function:: void EPNPEstimator::ChooseControlPoints()

.. code-block:: cpp

    void EPNPEstimator::ChooseControlPoints() {

      // 以C0作为质心参考点
      cws_[0].setZero();

      for (size_t i = 0; i < points3D_->size(); ++i) {
        cws_[0] += (*points3D_)[i];
      }

      cws_[0] /= points3D_->size();

      Eigen::Matrix<double, Eigen::Dynamic, 3> PW0(points3D_->size(), 3);

      for (size_t i = 0; i < points3D_->size(); ++i) {
        PW0.row(i) = (*points3D_)[i] - cws_[0];
      }

      const Eigen::Matrix3d PW0tPW0 = PW0.transpose() * PW0;

      Eigen::JacobiSVD<Eigen::Matrix3d> svd(
          PW0tPW0, Eigen::ComputeFullV | Eigen::ComputeFullU);

      const Eigen::Vector3d D = svd.singularValues();

      const Eigen::Matrix3d Ut = svd.matrixU().transpose();

      for (int i = 1; i < 4; ++i) {
        const double k = std::sqrt(D(i - 1) / points3D_->size());

        cws_[i] = cws_[0] + k * Ut.row(i - 1).transpose();
      }
    }

.. note::

    为了系统的稳定性，采用如下策略进行控制点的选取。第一个控制点选择在所有3D点的质心位置

    .. math::

        c_1^w = \frac{1}{n} \sum\limits_{i=1}^n p_i^w

    其余点选择在数据的主方向上。具体操作如下，计算矩阵

    .. math::

        A = \left[
        \begin{matrix}
        (p_1^w)^T-(c_1^w)^T\\
        \dots\\
        (p_n^w)^T-(c_1^w)^T
        \end{matrix}
        \right]

    计算 :math:`A^TA` 的3个特征值为  :math:`\lambda_1,\lambda_2,\lambda_3`， 对应的特征向量为 :math:`v_1,v_2,v_3`，那么剩下的三个控制点为：

    .. math::

        \begin{cases}
        c_2^w = c_1^w + \sqrt{ \frac{\lambda_1}{n} } v_1 \\
        c_3^w = c_1^w + \sqrt{ \frac{\lambda_2}{n} } v_2 \\
        c_4^w = c_1^w + \sqrt{ \frac{\lambda_3}{n} } v_3 \\
        \end{cases}

    上述操作实际上是找到点云的重心，以及点云的三个主方向。`主成分分析(PCA) <https://en.wikipedia.org/wiki/Principal_component_analysis>`_



    到目前为止，已知可以知道4个控制点在世界坐标系下的坐标  :math:`c_j` ，每一个3D点的hd坐标  :math:`\alpha_{ij}`  。如果能把4个控制点在相机坐标系下的坐标求解出来，就可以计算出3D点在相机坐标系下的坐标，就可以求解出外参数  :math:`[R|t]` 。

4. **ComputeBarycentricCoordinates**

   计算barycentric coodinates

   .. cpp:function:: bool EPNPEstimator::ComputeBarycentricCoordinates()

   .. code-block:: cpp

      bool EPNPEstimator::ComputeBarycentricCoordinates() {
        Eigen::Matrix3d CC;
        for (int i = 0; i < 3; ++i) {
          for (int j = 1; j < 4; ++j) {
            CC(i, j - 1) = cws_[j][i] - cws_[0][i];
          }
        }

        if (CC.colPivHouseholderQr().rank() < 3) {
          return false;
        }

        const Eigen::Matrix3d CC_inv = CC.inverse();

        alphas_.resize(points2D_->size());
        for (size_t i = 0; i < points3D_->size(); ++i) {
          for (int j = 0; j < 3; ++j) {
            alphas_[i][1 + j] = CC_inv(j, 0) * ((*points3D_)[i][0] - cws_[0][0]) +
                                CC_inv(j, 1) * ((*points3D_)[i][1] - cws_[0][1]) +
                                CC_inv(j, 2) * ((*points3D_)[i][2] - cws_[0][2]);
          }
          alphas_[i][0] = 1.0 - alphas_[i][1] - alphas_[i][2] - alphas_[i][3];
        }

        return true;
      }

   .. note::

      .. code-block:: cpp

         for (int i = 0; i < 3; ++i) {
            for (int j = 1; j < 4; ++j) {
               CC(i, j - 1) = cws_[j][i] - cws_[0][i];
            }
         }

      假设上一步得到的控制点为 :math:`X_i = (x_i, y_i, z_i)^T ~~~(i =  1, 2, 3, 4)`， 则：经过变换后（将第一个控制点移动到原点）的控制点坐标组成的矩阵为

      .. math::

         CC = \left[
         \begin{matrix}
         x_2 - x_1 & x_3-x_1 & x_4-x_1\\
         y_2 - y_1 & y_3-y_1 & y_4-y_1\\
         z_2 - z_1 & z_3-z_1 & z_4-z_1
         \end{matrix}
         \right]

      如果QR分解的矩阵的秩 < 3，则返回false

      .. code-block:: cpp

         if (CC.colPivHouseholderQr().rank() < 3) {
          return false;
        }

      由第一节的公式  :math:`p_i^w = \sum\limits_{j=1}^4 \alpha_{ij}c_j^w, ~~~ with \sum\limits_{j=1}^4 \alpha_{ij} = 1` 可知

      barycentric coodinates的计算公式为：

      .. math::

         \left[
         \begin{matrix}
         \alpha_{i1}\\ \alpha_{i2}\\ \alpha_{i3}\\ \alpha_{i4}\\
         \end{matrix}
         \right] = C^{-1}
         \left[
         \begin{matrix}
         p_i^w\\1
         \end{matrix}
         \right]

      程序与公式稍稍有些不同，作者选择计算 :math:`\alpha_{i2},\alpha_{i3},\alpha_{i4}`， 并由于 :math:`\sum\limits_{j=1}^4 \alpha_{ij} = 1` ， 所以 :math:`\alpha_{i1} = 1 - \alpha_{i2} - \alpha_{i3} - \alpha_{i4}`

      .. code-block:: cpp

        alphas_.resize(points2D_->size());
        for (size_t i = 0; i < points3D_->size(); ++i) {
          for (int j = 0; j < 3; ++j) {
            alphas_[i][1 + j] = CC_inv(j, 0) * ((*points3D_)[i][0] - cws_[0][0]) +
                                CC_inv(j, 1) * ((*points3D_)[i][1] - cws_[0][1]) +
                                CC_inv(j, 2) * ((*points3D_)[i][2] - cws_[0][2]);
          }
          alphas_[i][0] = 1.0 - alphas_[i][1] - alphas_[i][2] - alphas_[i][3];
        }

5. **ComputeM**

   .. cpp:function::Eigen::Matrix<double, Eigen::Dynamic, 12> EPNPEstimator::ComputeM()

   .. code-block:: cpp

      Eigen::Matrix<double, Eigen::Dynamic, 12> EPNPEstimator::ComputeM() {
        Eigen::Matrix<double, Eigen::Dynamic, 12> M(2 * points2D_->size(), 12);
        for (size_t i = 0; i < points3D_->size(); ++i) {
          for (size_t j = 0; j < 4; ++j) {
            M(2 * i, 3 * j) = alphas_[i][j];
            M(2 * i, 3 * j + 1) = 0.0;
            M(2 * i, 3 * j + 2) = -alphas_[i][j] * (*points2D_)[i].x();

            M(2 * i + 1, 3 * j) = 0.0;
            M(2 * i + 1, 3 * j + 1) = alphas_[i][j];
            M(2 * i + 1, 3 * j + 2) = -alphas_[i][j] * (*points2D_)[i].y();
          }
        }
        return M;
      }

   .. note::

      设 :math:`K` 是摄像头的内参矩阵，可以通过标定获得 :math:`\{u_i\}_{i=1,...,n}` 是参考点 :math:`\{p_i\}_{i=1,...,n}` 的2D投影，那么有

      .. math::

         \forall i, w_i \left[
         \begin{matrix}
         u_i\\1
         \end{matrix}
         \right] = Kp_i^c = K \sum\limits_{j=1}^4 \alpha_{ij} c_j^c

      用 :math:`c_j^c = [x_j^c, y_j^c, z_j^c]^T` 带入上式，而且把 :math:`K` ：

      .. math::

         \forall i, w_i \left[
         \begin{matrix}
         u_i\\v_i\\1
         \end{matrix}
         \right] = \left[
         \begin{matrix}
         f_u & 0 & u_c\\0 & f_v & v_c \\ 0 & 0 & 1
         \end{matrix}
         \right] \sum\limits_{j=1}^4 \alpha_{ij} \left[
         \begin{matrix}
         x_j^c\\ y_j^c \\ z_j^c
         \end{matrix}
         \right]

      从上式可以得到两个线性方程：

      .. math::

         \begin{cases}
         \sum\limits_{j=1}^4 \alpha_{ij}f_ux_j^c + \alpha_{ij}(u_c-u_i)z_j^c = 0\\
         \sum\limits_{j=1}^4 \alpha_{ij}f_vy_j^c + \alpha_{ij}(v_c-v_j)z_j^c = 0
         \end{cases}

      把所有 :math:`n` 个点串联起来，我们可以得到一个线性方程组：

      .. math::

         Mx = 0

   .. error::

      这里作者的代码忽略了内参，没看懂为什么？

