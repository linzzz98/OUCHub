EPnP
=====

EPNP求解器，用于解决PNP(Perspective-n-Point)问题。 求解器至少需要4个2D-3D对应关系（对于共面的情况只需要3对）。

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
   p_j^w \\ 1
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

   注意：在上面的推导中不难发现，同一3D点在世界坐标系下的 **齐次重心坐标** 与其在相机坐标系下的相同。这意味着，可以预先在世界坐标系下求取齐次重心坐标的 :math:`a_{ij}` ，然后将其作为已知量拿到相机坐标系下使用。

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

Estimate
------------------------

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

ComputePose
------------------------

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

ChooseControlPoints
------------------------

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

    .. figure:: 0.jpg
       :figclass: align-center

    到目前为止，已知可以知道4个控制点在世界坐标系下的坐标  :math:`c_j` ，每一个3D点的坐标  :math:`\alpha_{ij}`  。如果能把4个控制点在相机坐标系下的坐标求解出来，就可以计算出3D点在相机坐标系下的坐标，就可以求解出外参数  :math:`[R|t]` 。

ComputeBarycentricCoordinates
--------------------------------------------------

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

      假设上一步得到的控制点为 :math:`c_i^w = (x_i, y_i, z_i)^T ~~~(i =  1, 2, 3, 4)`， 则：经过变换后（将第一个控制点移动到原点）的控制点坐标组成的矩阵为

      .. math::

         CC = \left[
         \begin{matrix}
         x_2 - x_1 & x_3-x_1 & x_4-x_1\\
         y_2 - y_1 & y_3-y_1 & y_4-y_1\\
         z_2 - z_1 & z_3-z_1 & z_4-z_1
         \end{matrix}
         \right]

      其中 :math:`x_1` 为世界坐标系下的中心控制点， :math:`x_2,x_3,x_4` 为世界坐标系下的其他控制点

      如果QR分解的矩阵的秩 < 3，则返回false

      .. code-block:: cpp

         if (CC.colPivHouseholderQr().rank() < 3) {
          return false;
        }

      barycentric coodinates的计算公式为：

      .. math::

         \begin{eqnarray}
         \left[
         \begin{matrix}
         \alpha_{i2}\\ \alpha_{i3}\\ \alpha_{i4}\\
         \end{matrix}
         \right] &=& (CC)^{-1}
         \left[
         \begin{matrix}
         p_{ix}^w - c_{ix}^w\\p_{iy}^w - c_{iy}^w\\p_{iz}^w - c_{iz}^w
         \end{matrix}
         \right]\\\\
         \alpha_{i1} &=& 1 - \alpha_{i2} - \alpha_{i3} - \alpha_{i4} \\\\
         \end{eqnarray}

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

ComputeM
-------------------------
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

      用 :math:`c_j^c = [x_j^c, y_j^c, z_j^c]^T` 带入上式，把 :math:`K` 展开：

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

      已知变量： 控制参数 :math:`a_{ij}` ，相机内参数 :math:`f_x, f_y, c_x, c_y` ，  2D点坐标 :math:`u_i,v_i`

      未知变量： 4个控制点在相机坐标系下的坐标 :math:`x_j^c, y_j^c, z_j^c`

      因此  :math:`x` 是待求的12个位置参数， :math:`M` 的大小为 :math:`2n \times 12` ， :math:`Mx = 0` 的解即为 :math:`M` 的零空间。

      .. tip::

         直接对 :math:`Mx = 0` 使用SVD分解，其复杂度为 :math:`O(n^3)`

         对上式左右同乘 :math:`M^T` ，转换为对 :math:`M^TMx = 0` 进行奇异值分解，此时 :math:`M^TM` 为方阵，复杂度降为 :math:`O(n)`

      .. important::

         其中 :math:`x` 可以表示为 :math:`x = \sum\limits_{k = 1} ^N \beta_k v_k`

         这样表示的原因在于，由于 :math:`M` 的维数为 :math:`2 n * 12` ，则方程 :math:`Mx = 0` 的解的个数是根据 :math:`n` 来决定。

         如果 :math:`n >=6` 则方程在没有噪声的情况下有唯一解。

         如果 :math:`n < 6` 则方程有多个解，则此时 :math:`x` 由这些解的线性组合所决定，所以 :math:`x` 表示为：

         .. math::

            x = \sum\limits_{k = 1} ^N \beta_k v_k

         这里的 :math:`v_k` 是指的对矩阵 :math:`M^TM` 进行奇异值分解后，最小奇异值对应的特征向量，需要进行求解的是 :math:`\beta_k`

         经过作者的证明， :math:`N` 最多为 :math:`4` ，因此只需要考虑 :math:`N = 1,2,3,4` 这四种情况即可。

         （ :math:`N = 4` 时，方程为欠定方程组，在本章仅考虑 :math:`n = 1,2,3` 的情况）


   .. error::

      这里作者的代码忽略了内参，没看懂为什么？


ComputeL6x10
-------------------------

   .. cpp:function:: Eigen::Matrix<double, 6, 10> EPNPEstimator::ComputeL6x10(const Eigen::Matrix<double, 12, 12>& Ut)

   .. code-block:: cpp

      Eigen::Matrix<double, 6, 10> EPNPEstimator::ComputeL6x10(
          const Eigen::Matrix<double, 12, 12>& Ut) {
         Eigen::Matrix<double, 6, 10> L6x10;

         std::array<std::array<Eigen::Vector3d, 6>, 4> dv;
         for (int i = 0; i < 4; ++i) {
            int a = 0, b = 1;
            for (int j = 0; j < 6; ++j) {
               dv[i][j][0] = Ut(11 - i, 3 * a) - Ut(11 - i, 3 * b);
               dv[i][j][1] = Ut(11 - i, 3 * a + 1) - Ut(11 - i, 3 * b + 1);
               dv[i][j][2] = Ut(11 - i, 3 * a + 2) - Ut(11 - i, 3 * b + 2);

               b += 1;
            if (b > 3) {
               a += 1;
               b = a + 1;
            }
          }
        }

         for (int i = 0; i < 6; ++i) {
            L6x10(i, 0) = dv[0][i].transpose() * dv[0][i];
            L6x10(i, 1) = 2.0 * dv[0][i].transpose() * dv[1][i];
            L6x10(i, 2) = dv[1][i].transpose() * dv[1][i];
            L6x10(i, 3) = 2.0 * dv[0][i].transpose() * dv[2][i];
            L6x10(i, 4) = 2.0 * dv[1][i].transpose() * dv[2][i];
            L6x10(i, 5) = dv[2][i].transpose() * dv[2][i];
            L6x10(i, 6) = 2.0 * dv[0][i].transpose() * dv[3][i];
            L6x10(i, 7) = 2.0 * dv[1][i].transpose() * dv[3][i];
            L6x10(i, 8) = 2.0 * dv[2][i].transpose() * dv[3][i];
            L6x10(i, 9) = dv[3][i].transpose() * dv[3][i];
         }

         return L6x10;
      }

   .. note::

      由于控制点 :math:`c_i` 之间的距离是不随着坐标系的改变而改变的，因此有

      .. math::

         ||c_i^c - c_j^c||^2 = ||c_i^w - c_j^w||^2

      注意，上面一节的等式 :math:`Mx = 0` 中的 :math:`x` 是  :math:`c_i^c` ，因此上式转换为：

      .. math::

         ||\sum\limits_{k=1}^N \beta_k v_k^{[i]} - \sum\limits_{k=1}^N \beta_k v_k^{[j]}||^2 = ||c_i^w - c_j^w||^2

      这是一个关于 :math:`\{ \beta_k \}_{k=1,...,N}` 的二次方程，没有关于 :math:`\{ \beta_k \}_{k=1,...,N}` 的一次项。

      将二次项 :math:`\beta_i \beta_j` 替换为 :math:`\beta_{ij}` ，那么该方程就是 :math:`\{\beta_{ij}\}_{i,j=1,...,N}` 的线性方程。

      对于  :math:`v_j^{[i]}` ：

      * 下标 :math:`j` 表示该 :math:`v` 向量是 :math:`M^TM` 奇异值分解后的右奇异值矩阵的（ :math:`U` 矩阵）的倒数第 :math:`j` 列。

      * 上标 :math:`i` 是第 :math:`j` 列里的第 :math:`i` 个控制点。

      .. figure:: 1.jpg
         :figclass: align-center
         :scale: 60%

      .. important::

         对于4个控制点，可以得到 :math:`C_4^2 = 6` 个方程

         当 :math:`N` 取不同的值时，线性未知数的个数为：

         *  :math:`N = 1` ，线性未知数的个数为1，方程为变为 :math:`x = \beta v`

         .. math::

            || \beta v^{[i]} - \beta v^{[j]} ||^2 = ||c_i^w - c_j^w||^2

         *  :math:`N = 2` ，线性未知数的个数为3，方程为变为 :math:`x = \beta_1 v_1 + \beta_2 v_2`

         .. math::

            || (\beta_1 v_1^{[i]} + \beta_2 v_2^{[i]}) - (\beta_1 v_1^{[j]} + \beta_2 v_2^{[j]})||^2 = ||c_i^w - c_j^w||^2

         *  :math:`N = 3` ，线性未知数的个数为6，方程为变为 :math:`x = \beta_1 v_1 + \beta_2 v_2 + \beta_3 v_3`

         .. math::

            || (\beta_1 v_1^{[i]} + \beta_2 v_2^{[i]} + \beta_3 v_3^{[i]}) - (\beta_1 v_1^{[j]} + \beta_2 v_2^{[j]} + \beta_3 v_3^{[j]})||^2 = ||c_i^w - c_j^w||^2

         *  :math:`N = 4` ，线性未知数的个数为10，此时未知数个数多于方程个数（欠定方程）

         .. math::

            || (\beta_1 v_1^{[i]} + \beta_2 v_2^{[i]} + \beta_3 v_3^{[i]} + \beta_4 v_4^{[i]}) - (...) || = ||c_i^w - c_j^w||^2



      如何求解 :math:`\beta_k` 呢？

      *  :math:`N = 1` 时， :math:`\beta` 为：

         .. math::

            \beta = \frac{ \sum\limits_{\{i,j\}\in [1,4]}  ||v^{[i]} - v^{[j]} || · || c_i^w - c_j^w || }  {\sum\limits_{\{i,j\}\in[1,4] } || v^{[i]} - v^{[j]} ||^2 }

      *  :math:`N = 2` 时，将方程展开：

         .. math::

            || \beta_1 \underbrace{ (v_1^{[i]} - v_1^{[j]}) }_{S_1} + \beta_2 \underbrace{ (v_2^{[i]} - v_2^{[j]}) }_{S_2}||^2 = \underbrace{ || c_i^w - c_j^w ||^2 }_c\\

         .. math::

            \Downarrow

         .. math::

            \beta_1^2S_1^T S_1 + 2\beta_1\beta_2 S_2 + \beta_2^2 S_2^T S_2 = c

         根据之前定义的 :math:`\beta_{ij} = \beta_i \beta_j` ，从而 :math:`\beta_{11} = \beta_1 ^2, ~~\beta_{12} = \beta_1 * \beta_2, ~~\beta_{22} = \beta_2^2`

         进而方程变为：

         .. math::

            L \beta = \rho

         其中 :math:`\beta = [\beta_{11},\beta_{12},\beta_{22}]^T` ， :math:`L` 为 :math:`6\times 3` 的矩阵， :math:`\rho` 为 :math:`6 \times 1` 的矩阵。

         .. figure:: 2.jpg
            :scale: 60%

         此时， :math:`\beta` 为：

         .. math::

            \beta = (L^TL)^{-1}L^T \rho

         解出 :math:`\beta` 后可以获得两组 :math:`\beta_1, \beta_2` 的解，再根据控制点在相机前端，即 :math:`c_j^c ` 的 :math:`z > 0` ， 从而唯一确定 :math:`\beta_1, \beta_2`

      *  :math:`N = 3` 时，与 :math:`N = 2` 解法相同：

         此时 :math:`\beta = [\beta_{11},\beta_{12},\beta_{13},\beta_{22},\beta_{23},\beta_{33}]^T` ， :math:`L` 的大小为 :math:`6 \times 6`

         .. figure:: 3.jpg
            :scale: 60%

         此时， :math:`\beta` 为：

         .. math::

            \beta = L^{-1}\rho

      *  :math:`N = 4` 时，未知数的个数多于方程的个数

         论文中提到， :math:`\beta_{ab}\beta_{cd} = \beta_{a}\beta_{b}\beta_{c}\beta_{d} = \beta_{a'b'}\beta_{c'd'}`

         其中 :math:`\{a',b',c',d'\}` 是  :math:`\{a,b,c,d\}` 的一个排列。这样就可以减少未知数的个数。例如：

         例如：求出了 :math:`\beta_{11},\beta_{12},\beta_{13}` 那么就可以得到 :math:`\beta_{23} = \frac{\beta_{12}\beta_{13}}{\beta_{11}}` ，这样就可以求出 :math:`\{\beta_{ij}\}_{i,j = 1,...,N}` 了

         .. attention::

            注意：此时\beta 是 :math:`6 \times 10` 的（ :math:`\beta_{11} ··· \beta{44}` ），由于 :math:`\rho` 必须是 :math:`6\times 1` 因此 :math:`L` 的大小为 :math:`6 \times 10` 也就是代码中的 :math:`L6x10`

   .. note::

      回到代码，可以明显看到 :math:`N = 2,3,4` 的时候， :math:`L` 矩阵是 :math:`N = 4` 的情况下的 :math:`L` 矩阵的子集，因此直接构造  :math:`N = 4` 时的 :math:`L` 矩阵。

      .. tip::

         因为是 :math:`U^T` ，所以这里特征向量为 ``行向量``

         .. math::

            \begin{eqnarray}
            &Ut&(11,&[0,1,2]&) &\longrightarrow& ~~ v_1^{[1]}~~~~~~~~Ut(11,[9,10,11]) \longrightarrow  v_1^{[4]}\\
            &Ut&(10,&[0,1,2]&) &\longrightarrow& ~~ v_2^{[1]}\\
            &Ut&(9,&[0,1,2]&)  &\longrightarrow& ~~ v_3^{[1]}\\
            &Ut&(8,&[0,1,2]&)  &\longrightarrow& ~~ v_4^{[1]}
            \end{eqnarray}


         .. figure:: 4.jpg
            :figclass: align-center
            :scale: 60%

      .. code-block:: cpp

         Eigen::Matrix<double, 6, 10> L6x10;

         std::array<std::array<Eigen::Vector3d, 6>, 4> dv;

         for (int i = 0; i < 4; ++i) {
            int a = 0, b = 1;
            for (int j = 0; j < 6; ++j) {
               dv[i][j][0] = Ut(11 - i, 3 * a) - Ut(11 - i, 3 * b);
               dv[i][j][1] = Ut(11 - i, 3 * a + 1) - Ut(11 - i, 3 * b + 1);
               dv[i][j][2] = Ut(11 - i, 3 * a + 2) - Ut(11 - i, 3 * b + 2);

               b += 1;
               if (b > 3) {
                  a += 1;
                  b = a + 1;
               }
            }
         }

      则

      .. math::

         dv[i][0] = v_i^{[1]} - v_i^{[2]}~~~~~~~~dv[i][1] = v_i^{[1]} - v_i^{[3]}~~~~~~~~dv[i][2] = v_i^{[1]} - v_i^{[4]}\\
         dv[i][3] = v_i^{[2]} - v_i^{[3]}~~~~~~~~dv[i][4] = v_i^{[2]} - v_i^{[4]}~~~~~~~~dv[i][5] = v_i^{[3]} - v_i^{[4]}


      接下来需要构造的是 :math:`L` 矩阵

      .. parsed-literal::

                         L (6*10)                       *   betas (10*1)    =  rho (6*1)

         | ||v1i-v1j||^2  2*|(v1i-v1j)(v2i-v2j)|    ..|   | betas1*betas1 |   | dcw0_1 |
         |      ..                                    |   | betas1*betas2 |   | dcw0_2 |
         |      ..                                    |   | betas2*betas2 |   | dcw0_3 |
         |      ..                                    | * | betas1*betas3 | = | dcw1_2 |
         |      ..                                    |   | betas2*betas3 |   | dcw1_3 |
         |      ..                                    |   | betas3*betas3 |   | dcw2_3 |
                                                          | betas1*betas4 |
                                                          | betas2*betas4 |
                                                          | betas3*betas4 |
                                                          | betas4*betas4 |


      .. code-block:: cpp

         for (int i = 0; i < 6; ++i) {
            L6x10(i, 0) = dv[0][i].transpose() * dv[0][i];
            L6x10(i, 1) = 2.0 * dv[0][i].transpose() * dv[1][i];
            L6x10(i, 2) = dv[1][i].transpose() * dv[1][i];
            L6x10(i, 3) = 2.0 * dv[0][i].transpose() * dv[2][i];
            L6x10(i, 4) = 2.0 * dv[1][i].transpose() * dv[2][i];
            L6x10(i, 5) = dv[2][i].transpose() * dv[2][i];
            L6x10(i, 6) = 2.0 * dv[0][i].transpose() * dv[3][i];
            L6x10(i, 7) = 2.0 * dv[1][i].transpose() * dv[3][i];
            L6x10(i, 8) = 2.0 * dv[2][i].transpose() * dv[3][i];
            L6x10(i, 9) = dv[3][i].transpose() * dv[3][i];
         }

ComputeRho
-------------------------

   构造 :math:`6 \times 1` 的距离矩阵 :math:`\rho` ，记录4个控制点之间各自的距离

   .. cpp:function:: Eigen::Matrix<double, 6, 1> EPNPEstimator::ComputeRho()

   .. code-block:: cpp

      Eigen::Matrix<double, 6, 1> EPNPEstimator::ComputeRho() {
        Eigen::Matrix<double, 6, 1> rho;
        rho[0] = (cws_[0] - cws_[1]).squaredNorm();
        rho[1] = (cws_[0] - cws_[2]).squaredNorm();
        rho[2] = (cws_[0] - cws_[3]).squaredNorm();
        rho[3] = (cws_[1] - cws_[2]).squaredNorm();
        rho[4] = (cws_[1] - cws_[3]).squaredNorm();
        rho[5] = (cws_[2] - cws_[3]).squaredNorm();
        return rho;
      }

FindBetasApprox1
-------------------------

   求解 :math:`N = 4` 时的 :math:`\beta`

   .. important::

      注意！这里的程序，包括Opencv里的EPnP，都没有按照正确的方法去求解，而是选择了近似的方法。

      .. parsed-literal::

         betas10        = [B11 B12 B22 B13 B23 B33 B14 B24 B34 B44]

         betas_approx_1 = [B11 B12     B13         B14]

      将应该求的参数 :math:`betas \_10` 由10个减少到了4个 :math:`betas\_approx\_1` ， 然后求解的线性方程组。

   .. cpp:function:: void EPNPEstimator::FindBetasApprox1(const Eigen::Matrix<double, 6, 10>& L6x10,const Eigen::Matrix<double, 6, 1>& rho,Eigen::Vector4d* betas)

   .. code-block:: cpp

      void EPNPEstimator::FindBetasApprox1(const Eigen::Matrix<double, 6, 10>& L6x10,
                                           const Eigen::Matrix<double, 6, 1>& rho,
                                           Eigen::Vector4d* betas) {
         Eigen::Matrix<double, 6, 4> L_6x4;
         for (int i = 0; i < 6; ++i) {
            L_6x4(i, 0) = L6x10(i, 0);
            L_6x4(i, 1) = L6x10(i, 1);
            L_6x4(i, 2) = L6x10(i, 3);
            L_6x4(i, 3) = L6x10(i, 6);
         }

         Eigen::JacobiSVD<Eigen::Matrix<double, 6, 4>> svd(
               L_6x4, Eigen::ComputeFullV | Eigen::ComputeFullU);
         Eigen::Matrix<double, 6, 1> Rho_temp = rho;
         const Eigen::Matrix<double, 4, 1> b4 = svd.solve(Rho_temp);

         if (b4[0] < 0) {
            (*betas)[0] = std::sqrt(-b4[0]);
            (*betas)[1] = -b4[1] / (*betas)[0];
            (*betas)[2] = -b4[2] / (*betas)[0];
            (*betas)[3] = -b4[3] / (*betas)[0];
         } else {
            (*betas)[0] = std::sqrt(b4[0]);
            (*betas)[1] = b4[1] / (*betas)[0];
            (*betas)[2] = b4[2] / (*betas)[0];
            (*betas)[3] = b4[3] / (*betas)[0];
         }
      }

   .. note::

      求解线性方程组，求出 :math:`\beta_{11}, \beta_{12}, \beta_{13}, \beta_{14}`

      .. code-block:: cpp

         Eigen::JacobiSVD<Eigen::Matrix<double, 6, 4>> svd(
               L_6x4, Eigen::ComputeFullV | Eigen::ComputeFullU);

         Eigen::Matrix<double, 6, 1> Rho_temp = rho;

         const Eigen::Matrix<double, 4, 1> b4 = svd.solve(Rho_temp);

      然后求出 :math:`\beta_1, \beta_2, \beta_3, \beta_4`

      .. code-block:: cpp

         if (b4[0] < 0) {
            (*betas)[0] = std::sqrt(-b4[0]);
            (*betas)[1] = -b4[1] / (*betas)[0];
            (*betas)[2] = -b4[2] / (*betas)[0];
            (*betas)[3] = -b4[3] / (*betas)[0];
         }

         else {
            (*betas)[0] = std::sqrt(b4[0]);
            (*betas)[1] = b4[1] / (*betas)[0];
            (*betas)[2] = b4[2] / (*betas)[0];
            (*betas)[3] = b4[3] / (*betas)[0];
         }

FindBetasApprox2
-------------------------

   求解 :math:`N = 2` 时的 :math:`\beta`

   .. parsed-literal::

      betas10        = [B11 B12 B22 B13 B23 B33 B14 B24 B34 B44]

      betas_approx_2 = [B11 B12 B22                            ]

   .. cpp:function:: void EPNPEstimator::FindBetasApprox2(const Eigen::Matrix<double, 6, 10>& L6x10,const Eigen::Matrix<double, 6, 1>& rho,Eigen::Vector4d* betas)

   .. code-block:: cpp

      void EPNPEstimator::FindBetasApprox2(const Eigen::Matrix<double, 6, 10>& L6x10,
                                     const Eigen::Matrix<double, 6, 1>& rho,
                                     Eigen::Vector4d* betas) {
        Eigen::Matrix<double, 6, 3> L_6x3(6, 3);

        for (int i = 0; i < 6; ++i) {
          L_6x3(i, 0) = L6x10(i, 0);
          L_6x3(i, 1) = L6x10(i, 1);
          L_6x3(i, 2) = L6x10(i, 2);
        }

        Eigen::JacobiSVD<Eigen::Matrix<double, 6, 3>> svd(
            L_6x3, Eigen::ComputeFullV | Eigen::ComputeFullU);
        Eigen::Matrix<double, 6, 1> Rho_temp = rho;
        const Eigen::Matrix<double, 3, 1> b3 = svd.solve(Rho_temp);

        if (b3[0] < 0) {
          (*betas)[0] = std::sqrt(-b3[0]);
          (*betas)[1] = (b3[2] < 0) ? std::sqrt(-b3[2]) : 0.0;
        } else {
          (*betas)[0] = std::sqrt(b3[0]);
          (*betas)[1] = (b3[2] > 0) ? std::sqrt(b3[2]) : 0.0;
        }

        if (b3[1] < 0) {
          (*betas)[0] = -(*betas)[0];
        }

        (*betas)[2] = 0.0;
        (*betas)[3] = 0.0;
      }

   .. note::

      解线性方程组 求出 :math:`\beta_{11}, \beta_{12}, \beta_{22}`

      .. code-block:: cpp

         Eigen::JacobiSVD<Eigen::Matrix<double, 6, 3>> svd(
               L_6x3, Eigen::ComputeFullV | Eigen::ComputeFullU);

         Eigen::Matrix<double, 6, 1> Rho_temp = rho;

         const Eigen::Matrix<double, 3, 1> b3 = svd.solve(Rho_temp);

      然后再求出  :math:`\beta_1, \beta_2` （ :math:`\beta_3, \beta_4 = 0` ）

      .. code-block:: cpp

         if (b3[0] < 0) {
            (*betas)[0] = std::sqrt(-b3[0]);
            (*betas)[1] = (b3[2] < 0) ? std::sqrt(-b3[2]) : 0.0;
         }

         else {
            (*betas)[0] = std::sqrt(b3[0]);
            (*betas)[1] = (b3[2] > 0) ? std::sqrt(b3[2]) : 0.0;
         }

         if (b3[1] < 0) {
            (*betas)[0] = -(*betas)[0];
         }

         (*betas)[2] = 0.0;
         (*betas)[3] = 0.0;




FindBetasApprox3
-------------------------

   求解 :math:`N = 3` 时的 :math:`\beta`

   .. parsed-literal::

      betas10        = [B11 B12 B22 B13 B23 B33 B14 B24 B34 B44]

      betas_approx_3 = [B11 B12 B22 B13 B23                    ]

   .. cpp:function:: void EPNPEstimator::FindBetasApprox3(const Eigen::Matrix<double, 6, 10>& L6x10,const Eigen::Matrix<double, 6, 1>& rho,Eigen::Vector4d* betas)

   .. code-block:: cpp

      void EPNPEstimator::FindBetasApprox3(const Eigen::Matrix<double, 6, 10>& L6x10,
                                           const Eigen::Matrix<double, 6, 1>& rho,
                                           Eigen::Vector4d* betas) {
         Eigen::JacobiSVD<Eigen::Matrix<double, 6, 5>> svd(
            L6x10.leftCols<5>(), Eigen::ComputeFullV | Eigen::ComputeFullU);
         Eigen::Matrix<double, 6, 1> Rho_temp = rho;
         const Eigen::Matrix<double, 5, 1> b5 = svd.solve(Rho_temp);

         if (b5[0] < 0) {
            (*betas)[0] = std::sqrt(-b5[0]);
            (*betas)[1] = (b5[2] < 0) ? std::sqrt(-b5[2]) : 0.0;
         }

         else {
            (*betas)[0] = std::sqrt(b5[0]);
            (*betas)[1] = (b5[2] > 0) ? std::sqrt(b5[2]) : 0.0;
         }

         if (b5[1] < 0) {
            (*betas)[0] = -(*betas)[0];
         }

         (*betas)[2] = b5[3] / (*betas)[0];
         (*betas)[3] = 0.0;
      }

   .. note::

      解线性方程组 求出 :math:`\beta_{11}, \beta_{12}, \beta_{22}, \beta_{13}, \beta_{23}`

      .. code-block:: cpp

         Eigen::JacobiSVD<Eigen::Matrix<double, 6, 5>> svd(
               L6x10.leftCols<5>(), Eigen::ComputeFullV | Eigen::ComputeFullU);

         Eigen::Matrix<double, 6, 1> Rho_temp = rho;

         const Eigen::Matrix<double, 5, 1> b5 = svd.solve(Rho_temp);

      然后再求出  :math:`\beta_1, \beta_2, \beta_3` （ :math:`\beta_4 = 0` ）

      .. code-block:: cpp

         if (b5[0] < 0) {
            (*betas)[0] = std::sqrt(-b5[0]);
            (*betas)[1] = (b5[2] < 0) ? std::sqrt(-b5[2]) : 0.0;
         }

         else {
            (*betas)[0] = std::sqrt(b5[0]);
            (*betas)[1] = (b5[2] > 0) ? std::sqrt(b5[2]) : 0.0;
         }

         if (b5[1] < 0)
            (*betas)[0] = -(*betas)[0];

         (*betas)[2] = b5[3] / (*betas)[0];
         (*betas)[3] = 0.0;


RunGaussNewton
----------------------------

   在使用approx进行 :math:`\beta` 的初值求解后，需要使用GaussNewton的方法进行参数 :math:`\beta` 的优化。

   记：

   .. math::

      Error(\beta) = \sum\limits_{(i,j)~s.t.~i < j} (||c_i^c - c_j^c||^2 - ||c_i^w - c_j^w||^2)


   .. math::

      \Downarrow

   .. math::

      Error(\beta) = \sum\limits_{(i,j)~s.t.~i < j} (\sum\limits_{k=1}^4 || \beta_k v_k^{[i]} - \beta_k v_k^{[j]} ||^2 - ||c_i^w - c_j^w||^2)

   高斯牛顿法主要是要通过偏差对 :math:`\beta_1,\beta_2,\beta_3,\beta_4` 进行求导，这是数对矩阵的求导。

   .. math::

      Error(\beta_0 + \Delta \beta) = Error(\beta_0) + Error'(\beta) \Delta \beta = 0

   从而有等式：

   .. figure:: 6.jpg
      :figclass: align-center
      :scale: 75%

   这里分开来看：

   :math:`Error'(\beta)` ，称为 :math:`A` 矩阵。 实际上是 :math:`Error(\beta)` 分别对  :math:`\beta_i` 求偏导：

   .. math::

      \begin{eqnarray}
      A &=& [\frac{\delta Error(\beta)}{\delta \beta_1}~~~\frac{\delta Error(\beta)}{\delta \beta_2}~~~\frac{\delta Error(\beta)}{\delta \beta_3}~~~\frac{\delta Error(\beta)}{\delta \beta_4}]\\\\
        &=& [2L_1\beta_1+L_2\beta_2+L_4\beta_3+L_7\beta_4~~~ L_2\beta_1+2L_3\beta_2+L_5\beta_3+L_8\beta_4~~~···~~~···]
      \end{eqnarray}

   然后对 :math:`A` 矩阵进行 :math:`QR` 分解，得到：

   .. math::

      \Delta \beta = x = R^{-1} Q^{-1} b

   进而进行迭代：

   .. math::

      \beta' = \beta_0 + \Delta \beta


   .. cpp:function:: void EPNPEstimator::RunGaussNewton(const Eigen::Matrix<double, 6, 10>& L6x10,const Eigen::Matrix<double, 6, 1>& rho,Eigen::Vector4d* betas)

   .. code-block:: cpp

      void EPNPEstimator::RunGaussNewton(const Eigen::Matrix<double, 6, 10>& L6x10,
                                   const Eigen::Matrix<double, 6, 1>& rho,
                                   Eigen::Vector4d* betas) {
        Eigen::Matrix<double, 6, 4> A;
        Eigen::Matrix<double, 6, 1> b;

        const int kNumIterations = 5;
        for (int k = 0; k < kNumIterations; ++k) {
            for (int i = 0; i < 6; ++i) {
               A(i, 0) = 2 * L6x10(i, 0) * (*betas)[0] + L6x10(i, 1) * (*betas)[1] +
                      L6x10(i, 3) * (*betas)[2] + L6x10(i, 6) * (*betas)[3];
               A(i, 1) = L6x10(i, 1) * (*betas)[0] + 2 * L6x10(i, 2) * (*betas)[1] +
                      L6x10(i, 4) * (*betas)[2] + L6x10(i, 7) * (*betas)[3];
               A(i, 2) = L6x10(i, 3) * (*betas)[0] + L6x10(i, 4) * (*betas)[1] +
                      2 * L6x10(i, 5) * (*betas)[2] + L6x10(i, 8) * (*betas)[3];
               A(i, 3) = L6x10(i, 6) * (*betas)[0] + L6x10(i, 7) * (*betas)[1] +
                      L6x10(i, 8) * (*betas)[2] + 2 * L6x10(i, 9) * (*betas)[3];

               b(i) = rho[i] - (L6x10(i, 0) * (*betas)[0] * (*betas)[0] +
                              L6x10(i, 1) * (*betas)[0] * (*betas)[1] +
                              L6x10(i, 2) * (*betas)[1] * (*betas)[1] +
                              L6x10(i, 3) * (*betas)[0] * (*betas)[2] +
                              L6x10(i, 4) * (*betas)[1] * (*betas)[2] +
                              L6x10(i, 5) * (*betas)[2] * (*betas)[2] +
                              L6x10(i, 6) * (*betas)[0] * (*betas)[3] +
                              L6x10(i, 7) * (*betas)[1] * (*betas)[3] +
                              L6x10(i, 8) * (*betas)[2] * (*betas)[3] +
                              L6x10(i, 9) * (*betas)[3] * (*betas)[3]);
            }

            const Eigen::Vector4d x = A.colPivHouseholderQr().solve(b);

            (*betas) += x;
         }
      }

   .. note::

      结合代码来看，设定迭代次数为5次

      .. code-block:: cpp

         const int kNumIterations = 5;

      由于 :math:`L` 是 :math:`6 \times 10` 的矩阵，因此对每一行先进行求解。

      .. math::

         L(i,0) * b[0] + L(i,1) * b[1] + ... + L(i,9) * b[9] = r[i]

      那么对于 :math:`\beta_1` 求偏导，只有 :math:`b[0],b[1],b[3],b[6]` 含有 :math:`\beta_1` 项，剩下的项对 :math:`\beta_1` 求偏导后均为 :math:`0`

      因此  :math:`A(i,0)` 是 :math:`Error_{ij}(\beta)` 对 :math:`\beta_1` 求偏导：

      .. math::

         \begin{eqnarray}
         A(i,0) &=& \frac{\delta L(i,0) * \beta_1^2}{\delta \beta_1} + \frac{\delta L(i,1) * \beta_1 \beta_2}{\delta \beta_1} + \frac{\delta L(i,3) * \beta_1\beta_3}{\delta \beta_1} + \frac{\delta L(i,6) * \beta_1\beta_4}{\delta \beta_1}
         \\\\&=& 2 * L(i,0) * \beta_1 + L(i,1) * \beta_2 + L(i,3) * \beta_3 + L(i, 6) * \beta_4
         \end{eqnarray}

      .. parsed-literal::

                         L (6*10)                       *   betas (10*1)    =  rho (6*1)

         | ||v1i-v1j||^2  2*|(v1i-v1j)(v2i-v2j)|    ..|   | betas1*betas1 |   | dcw0_1 |
         |      ..                                    |   | betas1*betas2 |   | dcw0_2 |
         |      ..                                    |   | betas2*betas2 |   | dcw0_3 |
         |      ..                                    | * | betas1*betas3 | = | dcw1_2 |
         |      ..                                    |   | betas2*betas3 |   | dcw1_3 |
         |      ..                                    |   | betas3*betas3 |   | dcw2_3 |
                                                          | betas1*betas4 |
                                                          | betas2*betas4 |
                                                          | betas3*betas4 |
                                                          | betas4*betas4 |

      .. code-block:: cpp

         A(i, 0) = 2 * L6x10(i, 0) * (*betas)[0] + L6x10(i, 1) * (*betas)[1] +
                  L6x10(i, 3) * (*betas)[2] + L6x10(i, 6) * (*betas)[3];

         A(i, 1) = L6x10(i, 1) * (*betas)[0] + 2 * L6x10(i, 2) * (*betas)[1] +
                  L6x10(i, 4) * (*betas)[2] + L6x10(i, 7) * (*betas)[3];

         A(i, 2) = L6x10(i, 3) * (*betas)[0] + L6x10(i, 4) * (*betas)[1] +
                  2 * L6x10(i, 5) * (*betas)[2] + L6x10(i, 8) * (*betas)[3];

         A(i, 3) = L6x10(i, 6) * (*betas)[0] + L6x10(i, 7) * (*betas)[1] +
                  L6x10(i, 8) * (*betas)[2] + 2 * L6x10(i, 9) * (*betas)[3];


      方程 :math:`Ax = b` 的右侧 :math:`b` 为 :math:`\rho - L \beta_0`，使用的是Approx求出的初值 :math:`\beta_0`

      .. code-block:: cpp

         b(i) = rho[i] - (L6x10(i, 0) * (*betas)[0] * (*betas)[0] +
                        L6x10(i, 1) * (*betas)[0] * (*betas)[1] +
                        L6x10(i, 2) * (*betas)[1] * (*betas)[1] +
                        L6x10(i, 3) * (*betas)[0] * (*betas)[2] +
                        L6x10(i, 4) * (*betas)[1] * (*betas)[2] +
                        L6x10(i, 5) * (*betas)[2] * (*betas)[2] +
                        L6x10(i, 6) * (*betas)[0] * (*betas)[3] +
                        L6x10(i, 7) * (*betas)[1] * (*betas)[3] +
                        L6x10(i, 8) * (*betas)[2] * (*betas)[3] +
                        L6x10(i, 9) * (*betas)[3] * (*betas)[3]);

      然后通过 :math:`QR` 分解得到 :math:`\Delta \beta` ，加到 :math:`\beta` 上进行迭代

      .. code-block:: cpp

         const Eigen::Vector4d x = A.colPivHouseholderQr().solve(b);

         (*betas) += x;

ComputeRT
----------------------

   .. cpp:function:: double EPNPEstimator::ComputeRT(const Eigen::Matrix<double, 12, 12>& Ut,const Eigen::Vector4d& betas,Eigen::Matrix3d* R, Eigen::Vector3d* t)

   .. code-block:: cpp

      double EPNPEstimator::ComputeRT(const Eigen::Matrix<double, 12, 12>& Ut,
                                const Eigen::Vector4d& betas,
                                Eigen::Matrix3d* R, Eigen::Vector3d* t) {

         // 计算控制点在相机坐标系下的坐标
         ComputeCcs(betas, Ut);

         // 计算3D参考点在摄像头参考坐标系下的坐标
         ComputePcs();

         // 保证pcs和ccs坐标非负
         SolveForSign();

         //
         EstimateRT(R, t);

         return ComputeTotalReprojectionError(*R, *t);
      }

   .. note::

      通过带入 :math:`\beta` 的值到 :math:`x = \sum\limits_{i=1}^N \beta_i v_i ` 中得到相机坐标系下的四个控制点坐标 :math:`c_i^c` ，然后通过控制点的系数 :math:`\alpha_{ij}` 计算相机坐标系下参考点坐标 :math:`p_i^c` 。

      得到的坐标需要使深度值为正数所以得对符号进行处理。

      .. important::

         有了相机坐标系和世界坐标系的对应点就是3D-3D，就可以使用ICP进行求解。

         |:point_right:| :doc:`SVD求解ICP方法 </pages/paper/pointcloud/Least_Squares_Fitting/Least_Squares_Fitting>`

      求解 :math:`R, t` 的步骤为：

      1. 计算控制点在相机坐标系下的坐标

         .. math::

            c_i^c = \sum\limits_{j=1}^N \beta_k v_k^{[i]}, i = 1, ..., 4

         .. code-block:: cpp

            void EPNPEstimator::ComputeCcs(const Eigen::Vector4d& betas,
                               const Eigen::Matrix<double, 12, 12>& Ut) {
               for (int i = 0; i < 4; ++i) {
                  ccs_[i][0] = ccs_[i][1] = ccs_[i][2] = 0.0;
               }

               for (int i = 0; i < 4; ++i) {
                  for (int j = 0; j < 4; ++j) {
                     for (int k = 0; k < 3; ++k) {
                        ccs_[j][k] += betas[i] * Ut(11 - i, 3 * j + k);
                     }
                  }
               }
            }

      2. 计算3d点在相机坐标系下的坐标

         .. math::

            p_i^c = \sum\limits_{j=1}^4 \alpha_{ij}c_j^c, i = 1,...,n

         .. code-block:: cpp

            void EPNPEstimator::ComputePcs() {
              pcs_.resize(points2D_->size());
              for (size_t i = 0; i < points3D_->size(); ++i) {
                for (int j = 0; j < 3; ++j) {
                  pcs_[i][j] = alphas_[i][0] * ccs_[0][j] + alphas_[i][1] * ccs_[1][j] +
                               alphas_[i][2] * ccs_[2][j] + alphas_[i][3] * ccs_[3][j];
                }
              }
            }

      3. 保证pcs和ccs坐标非负

         检查第一个相机坐标系下的3d点，若发现深度为负，则调整所有ccs和所有pcs使其坐标非负。

         .. code-block:: cpp

            void EPNPEstimator::SolveForSign() {
              if (pcs_[0][2] < 0.0) {
                for (int i = 0; i < 4; ++i) {
                  ccs_[i] = -ccs_[i];
                }
                for (size_t i = 0; i < points3D_->size(); ++i) {
                  pcs_[i] = -pcs_[i];
                }
              }
            }

      4. 计算R和t

         EstimateRT

      5. 计算重投影误差并返回其值

         ComputeTotalReprojectionError


EstimateRT
----------------

   该步骤是使用的ICP求解 :math:`R,t`

   .. cpp:function:: void EPNPEstimator::EstimateRT(Eigen::Matrix3d* R, Eigen::Vector3d* t)

   .. code-block::

      void EPNPEstimator::EstimateRT(Eigen::Matrix3d* R, Eigen::Vector3d* t) {
        Eigen::Vector3d pc0 = Eigen::Vector3d::Zero();
        Eigen::Vector3d pw0 = Eigen::Vector3d::Zero();

        for (size_t i = 0; i < points3D_->size(); ++i) {
          pc0 += pcs_[i];
          pw0 += (*points3D_)[i];
        }
        pc0 /= points3D_->size();
        pw0 /= points3D_->size();

        Eigen::Matrix3d abt = Eigen::Matrix3d::Zero();
        for (size_t i = 0; i < points3D_->size(); ++i) {
          for (int j = 0; j < 3; ++j) {
            abt(j, 0) += (pcs_[i][j] - pc0[j]) * ((*points3D_)[i][0] - pw0[0]);
            abt(j, 1) += (pcs_[i][j] - pc0[j]) * ((*points3D_)[i][1] - pw0[1]);
            abt(j, 2) += (pcs_[i][j] - pc0[j]) * ((*points3D_)[i][2] - pw0[2]);
          }
        }

        Eigen::JacobiSVD<Eigen::Matrix3d> svd(
            abt, Eigen::ComputeFullV | Eigen::ComputeFullU);
        const Eigen::Matrix3d abt_U = svd.matrixU();
        const Eigen::Matrix3d abt_V = svd.matrixV();

        for (int i = 0; i < 3; ++i) {
          for (int j = 0; j < 3; ++j) {
            (*R)(i, j) = abt_U.row(i) * abt_V.row(j).transpose();
          }
        }

        if (R->determinant() < 0) {
          Eigen::Matrix3d Abt_v_prime = abt_V;
          Abt_v_prime.col(2) = -abt_V.col(2);
          for (int i = 0; i < 3; ++i) {
            for (int j = 0; j < 3; ++j) {
              (*R)(i, j) = abt_U.row(i) * Abt_v_prime.row(j).transpose();
            }
          }
        }

        *t = pc0 - *R * pw0;
      }

   .. note::

      1. 计算世界坐标系和相机坐标系下的质心坐标

         .. math::

            p_0^w = \frac{1}{n} \sum\limits_{i=1}^n p_i^w

         .. math::

            p_0^c = \frac{1}{n} \sum\limits_{i=1}^n p_i^c

         .. code-block:: cpp

            for (size_t i = 0; i < points3D_->size(); ++i) {
               pc0 += pcs_[i];
               pw0 += (*points3D_)[i];
            }

            pc0 /= points3D_->size();
            pw0 /= points3D_->size();

      2. 计算世界坐标系和相机坐标系去除质心的矩阵 :math:`A,B`

         .. math::

            A = \left[
            \begin{matrix}
            p_1^{w^T} - p_0^{w^T}\\···\\p_n^{w^T} - p_0^{w^T}
            \end{matrix}
            \right]

         .. math::

            B = \left[
            \begin{matrix}
            p_1^{c^T} - p_0^{c^T}\\···\\p_n^{c^T} - p_0^{c^T}
            \end{matrix}
            \right]


      3. 计算 :math:`W` 矩阵

         .. math::

            W = B^T A

         .. code-block:: cpp

            Eigen::Matrix3d abt = Eigen::Matrix3d::Zero();
            for (size_t i = 0; i < points3D_->size(); ++i) {
               for (int j = 0; j < 3; ++j) {
                  abt(j, 0) += (pcs_[i][j] - pc0[j]) * ((*points3D_)[i][0] - pw0[0]);
                  abt(j, 1) += (pcs_[i][j] - pc0[j]) * ((*points3D_)[i][1] - pw0[1]);
                  abt(j, 2) += (pcs_[i][j] - pc0[j]) * ((*points3D_)[i][2] - pw0[2]);
               }
            }

      4. 对 :math:`W` 进行SVD分解  :math:`W = U \Sigma V^T`

         .. code-block:: cpp

           Eigen::JacobiSVD<Eigen::Matrix3d> svd(abt, Eigen::ComputeFullV | Eigen::ComputeFullU);

      5. 计算旋转 :math:`R`

         .. math::

            R = UV^T

         .. code-block:: cpp

            const Eigen::Matrix3d abt_U = svd.matrixU();
            const Eigen::Matrix3d abt_V = svd.matrixV();

            for (int i = 0; i < 3; ++i)
               for (int j = 0; j < 3; ++j)
                  (*R)(i, j) = abt_U.row(i) * abt_V.row(j).transpose();

         如果 :math:`|R| < 0` ，则 :math:`R(2,:) = -R(2:0)`

         .. code-block:: cpp

            if (R->determinant() < 0) {
               Eigen::Matrix3d Abt_v_prime = abt_V;

               Abt_v_prime.col(2) = -abt_V.col(2);

               for (int i = 0; i < 3; ++i)
                  for (int j = 0; j < 3; ++j)
                     (*R)(i, j) = abt_U.row(i) * Abt_v_prime.row(j).transpose();
            }

      6. 计算平移 :math:`t` :

         .. math::

            t = p_0^c - Rp_0^w

         .. code-block:: cpp

            *t = pc0 - *R * pw0;


ComputeTotalReprojectionError
----------------------------------

   通过计算出的 :math:`R,t` 组成位姿矩阵，来计算2D点和3D点之间的重投影平方误差

   .. cpp:function:: double EPNPEstimator::ComputeTotalReprojectionError(const Eigen::Matrix3d& R, const Eigen::Vector3d& t)

   .. code-block:: cpp

      double EPNPEstimator::ComputeTotalReprojectionError(const Eigen::Matrix3d& R,
                                                          const Eigen::Vector3d& t) {
         Eigen::Matrix3x4d proj_matrix;
         proj_matrix.leftCols<3>() = R;
         proj_matrix.rightCols<1>() = t;

         std::vector<double> residuals;
         ComputeSquaredReprojectionError(*points2D_, *points3D_, proj_matrix,
                                        &residuals);

         double reproj_error = 0.0;
         for (const double residual : residuals) {
            reproj_error += std::sqrt(residual);
         }

         return reproj_error;
      }

