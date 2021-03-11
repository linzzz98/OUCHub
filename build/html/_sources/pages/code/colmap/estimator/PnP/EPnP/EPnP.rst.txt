.. default-domain:: cpp
.. default-domain:: cpp

EPnP
=====

EPNP求解器，用于解决PNP(透视N点)问题。 求解器至少需要4个2D-3D对应关系。

.. parsed-literal::

    \ `Epnp: An accurate o (n) solution to the pnp problem <http://www.iri.upc.edu/people/fmoreno/Publications/2009/pdf/Lepetit_ijcv2009.pdf>`_

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