FundmentalMatrix
==================

7点算法是指使用7个对应点估计基础矩阵，在一般情况下，7个点是能够估计基础矩阵所需要的最少点对应数。

使用7个点对应可得到下述方程：

.. math::

   Af = \left[
   \begin{matrix}
   u_1'u_1 & u_1'v_1 & u_1' & v_1'u_1 & v_1'v_1 & v_1' & u_1 & v_1 & 1\\
    &  &  &  \vdots &  &  &  & \\
   u_7'u_7 & u_7'v_7 & u_7' & v_7'u_7 & v_7'v_7 & v_7' & u_7 & v_7 & 1
   \end{matrix}
   \right] f = 0

一般地，系数矩阵 :math:`A` 的秩为7，上述方程的解集是9维空间中的通过坐标原点的一张2维平面。

令 :math:`f_1,f_2` 是方程的两个单位正交解，则它们的单位解集合是一个单参数簇 :math:`f = sf_1 + (1-s) f_2` ，于是基础矩阵可以表示为：

.. math::

   F = sF_1 + (1-s)F_2

其中 :math:`F_1,F_2` 是由 :math:`f_1, f_2` 确定的3阶矩阵。由于基本矩阵的秩为2，因此获得参数 :math:`s` 的一个约束矩阵：

.. math::

   det(sF_1 + (1-s)F_2) = 0

这是一个关于参数 :math:`s` 的3次方程，因此有1个解或3个解（如果由复解则删去，因为基础矩阵是一个实矩阵）

.. note::

   * 使用7个点对应，基础矩阵有一个解或三个可能的解

      * 当得到1个实数解、2个虚数解时，直接舍弃虚数解，实数解就是F的唯一解

      * 当得到3个实数解时，称之为 ``critical condition`` ,这意味着， :math:`F` 的7个点和两个相机中心点，这9个点通过三维空间中某个特定曲面。在这种特定情况下，7个对应点不能唯一确定一个 :math:`F`

   * 若图像中仅有7个对应点，当基础矩阵有3个解时，不能断定哪一个是真解。如果图像中有多于7个点对应，当基础矩阵有3个解时，可选取匹配点对应数最多的矩阵作为基础矩阵的真解



成员变量
-------------------------

1. 视角1下的特征点

   .. cpp:type:: Eigen::Vector2d FundamentalMatrixSevenPointEstimator::X_t;

2. 视角2下的特征点

    .. cpp:type:: Eigen::Vector2d FundamentalMatrixSevenPointEstimator::Y_t;

3. 基础矩阵

    .. cpp:type:: Eigen::Matrix3d FundamentalMatrixSevenPointEstimator::M_t;

4. 估计模型所需的最少样本数

    .. cpp:member:: static const int FundamentalMatrixSevenPointEstimator::kMinNumSamples = 7;

成员函数
-------------------------

1. **Estimate**

   从一组相应的点估计1或3个可能的基本矩阵的解。对应点的数量必须正好为7对。

   .. cpp:function:: static std::vector<M_t> FundamentalMatrixSevenPointEstimator::Estimate(const std::vector<X_t>& points1, const std::vector<Y_t>& points2);

   .. code-block:: cpp

      std::vector<FundamentalMatrixSevenPointEstimator::M_t> FundamentalMatrixSevenPointEstimator::Estimate(
          const std::vector<X_t>& points1, const std::vector<Y_t>& points2) {
        CHECK_EQ(points1.size(), 7);
        CHECK_EQ(points2.size(), 7);

        // 此处无需对这些点进行归一化。

        // 设置方程 [points2(i,:), 1]' * F * [points1(i,:), 1]'.
        Eigen::Matrix<double, 7, 9> A;
        for (size_t i = 0; i < 7; ++i) {
          const double x0 = points1[i](0);
          const double y0 = points1[i](1);
          const double x1 = points2[i](0);
          const double y1 = points2[i](1);
          A(i, 0) = x1 * x0;
          A(i, 1) = x1 * y0;
          A(i, 2) = x1;
          A(i, 3) = y1 * x0;
          A(i, 4) = y1 * y0;
          A(i, 5) = y1;
          A(i, 6) = x0;
          A(i, 7) = y0;
          A(i, 8) = 1;
        }

        // 9 unknowns with 7 equations, so we have 2D null space.
        Eigen::JacobiSVD<Eigen::Matrix<double, 7, 9>> svd(A, Eigen::ComputeFullV);
        const Eigen::Matrix<double, 9, 9> f = svd.matrixV();
        Eigen::Matrix<double, 1, 9> f1 = f.col(7);
        Eigen::Matrix<double, 1, 9> f2 = f.col(8);

        f1 -= f2;

        // Normalize, such that lambda + mu = 1
        // and add constraint det(F) = det(lambda * f1 + (1 - lambda) * f2).

        const double t0 = f1(4) * f1(8) - f1(5) * f1(7);
        const double t1 = f1(3) * f1(8) - f1(5) * f1(6);
        const double t2 = f1(3) * f1(7) - f1(4) * f1(6);
        const double t3 = f2(4) * f2(8) - f2(5) * f2(7);
        const double t4 = f2(3) * f2(8) - f2(5) * f2(6);
        const double t5 = f2(3) * f2(7) - f2(4) * f2(6);

        Eigen::Vector4d coeffs;
        coeffs(0) = f1(0) * t0 - f1(1) * t1 + f1(2) * t2;
        coeffs(1) = f2(0) * t0 - f2(1) * t1 + f2(2) * t2 -
                    f2(3) * (f1(1) * f1(8) - f1(2) * f1(7)) +
                    f2(4) * (f1(0) * f1(8) - f1(2) * f1(6)) -
                    f2(5) * (f1(0) * f1(7) - f1(1) * f1(6)) +
                    f2(6) * (f1(1) * f1(5) - f1(2) * f1(4)) -
                    f2(7) * (f1(0) * f1(5) - f1(2) * f1(3)) +
                    f2(8) * (f1(0) * f1(4) - f1(1) * f1(3));
        coeffs(2) = f1(0) * t3 - f1(1) * t4 + f1(2) * t5 -
                    f1(3) * (f2(1) * f2(8) - f2(2) * f2(7)) +
                    f1(4) * (f2(0) * f2(8) - f2(2) * f2(6)) -
                    f1(5) * (f2(0) * f2(7) - f2(1) * f2(6)) +
                    f1(6) * (f2(1) * f2(5) - f2(2) * f2(4)) -
                    f1(7) * (f2(0) * f2(5) - f2(2) * f2(3)) +
                    f1(8) * (f2(0) * f2(4) - f2(1) * f2(3));
        coeffs(3) = f2(0) * t3 - f2(1) * t4 + f2(2) * t5;

        Eigen::VectorXd roots_real;
        Eigen::VectorXd roots_imag;
        if (!FindPolynomialRootsCompanionMatrix(coeffs, &roots_real, &roots_imag)) {
          return {};
        }

        std::vector<M_t> models;
        models.reserve(roots_real.size());

        for (Eigen::VectorXd::Index i = 0; i < roots_real.size(); ++i) {
          const double kMaxRootImag = 1e-10;
          if (std::abs(roots_imag(i)) > kMaxRootImag) {
            continue;
          }

          const double lambda = roots_real(i);
          const double mu = 1;

          Eigen::MatrixXd F = lambda * f1 + mu * f2;

          F.resize(3, 3);

          const double kEps = 1e-10;
          if (std::abs(F(2, 2)) < kEps) {
            continue;
          }

          F /= F(2, 2);

          models.push_back(F.transpose());
        }

        return models;
      }

.. error::
   程序没看懂！！！ |:sob:|

