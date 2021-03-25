FundmentalMatrix
==================

七点算法
---------------

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
~~~~~~~~~~~~~~~~

1. 视角1下的特征点

   .. cpp:type:: Eigen::Vector2d FundamentalMatrixSevenPointEstimator::X_t;

2. 视角2下的特征点

   .. cpp:type:: Eigen::Vector2d FundamentalMatrixSevenPointEstimator::Y_t;

3. 基础矩阵

   .. cpp:type:: Eigen::Matrix3d FundamentalMatrixSevenPointEstimator::M_t;

4. 估计模型所需的最少样本数

   .. cpp:member:: static const int FundamentalMatrixSevenPointEstimator::kMinNumSamples = 7;

成员函数
~~~~~~~~~~~~~~~

Estimate
^^^^^^^^^^^^

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


Residuals
^^^^^^^^^^^^^^^^

   计算一组对应点和给定基本矩阵的残差（使用SamponError）

   .. cpp:function:: void FundamentalMatrixSevenPointEstimator::Residuals(const std::vector<X_t>& points1, const std::vector<Y_t>& points2,const M_t& F, std::vector<double>* residuals)

   .. code-block:: cpp

      void FundamentalMatrixSevenPointEstimator::Residuals(
            const std::vector<X_t>& points1, const std::vector<Y_t>& points2,
            const M_t& F, std::vector<double>* residuals) {
         ComputeSquaredSampsonError(points1, points2, F, residuals);
      }



归一化八点算法
---------------

算法步骤
~~~~~~~~~~

   :1. 归一化:

      根据 :math:`\hat{x_i} = Tx_i, \hat{x_i'} = T'x_i'` 变换图像坐标。其中 :math:`T,T'` 是由平移和缩放组成的归一化变换

   :2. 求解对应匹配的基本矩阵:

      **求线性解**：用由对应点集 :math:`\{\hat{x_i} \leftrightarrow \hat{x_i'} \}` 确定的系数矩阵 :math:`\hat{A}` 的最小奇异值的奇异向量确定 :math:`\hat{F}`

      **奇异值约束**：用SVD对 :math:`\hat{F}` 进行分解，强制约束其最小的奇异值为 :math:`0` ，得到 :math:`\hat{F'}` ，使得 :math:`det(\hat{F}') = 0`

   :3. 解除归一化:

      令 :math:`F = T'^T \hat{F}' T` ，矩阵 :math:`F` 就是 :math:`x_i \leftrightarrow x_i'` 对应的基础矩阵

基本矩阵由下述方程定义：

   .. math::

      x'^T F x = 0

其中 :math:`x \leftrightarrow x'` 是两幅图像的任意一对匹配点。

对应的方程为：

.. math::

   [x~~~y~~~1] \left[
   \begin{matrix}
   f_{11} & f_{12} & f_{13}\\
   f_{21} & f_{22} & f_{23}\\
   f_{31} & f_{32} & f_{33}
   \end{matrix}
   \right] \left[
   \begin{matrix}
   x'\\y'\\1
   \end{matrix}
   \right] = 0

展开写成列向量为：

.. math::

   [x'x~~~x'y~~~x'~~~y'x~~~y'y~~~y'~~~x~~~y~~~1] f = 0

给定n组点构造方程：

.. math::

   Af = \left[
   \begin{matrix}
   x_1'x_1 & x_1'y_1 & x_1' & y_1'x_1 & y_1'y_1 & y_1' & x_1 & y_1 & 1\\
   \vdots & \vdots & \vdots & \vdots & \vdots & \vdots & \vdots & \vdots\\
   x_n'x_n & x_n'y_n & x_n' & y_n'x_n & y_n'y_n & y_n' & x_n & y_n & 1
   \end{matrix}
   \right]f = 0

.. note::

   如果 :math:`A` 的秩恰好为8，则 :math:`f` 存在唯一解，可以通过线性算法求解 :math:`f` ，在差一个尺度因子的情况下解是唯一的。

   但是由于存在噪声，需要构建多于8对点的对应关系，构建一个超定方程，需要通过最小二乘法求解。

使用SVD分解， :math:`f` 的解是系数矩阵 :math:`A` 最小特征值对应的奇异向量，也就是对 :math:`A` 进行奇异值分解后 :math:`A = U\Sigma V^T` 中矩阵 :math:`V` 的最后一行列向量。

.. note::

   实质是解矢量 :math:`f` 在约束 :math:`||f||` 下取 :math:`||Af||` 最小的解

由于基本矩阵的奇异性，上述方法求得的 :math:`f` 转换的 :math:`F` 一般不满足秩为2的约束，需要进行修正。

如果矩阵非奇异，则计算的对极线将不重合。

在八点算法求解基本矩阵后，会增加一个奇异性约束，需要将奇异值由3个修正为2个

步骤为：使用SVD对F进行分解，强制约束最小的奇异值为0，再使用 :math:`F‘ = U\Sigma 'V` 代替原 :math:`F`

.. note::

   **解除归一化**

      .. math::

         &&\hat{x} = Tx,~~~\hat{x}' = T'x'\\\\
         &\Rightarrow& (\hat{x}')^T F \hat{x} = 0\\\\
         &\Rightarrow& (T'x')^TF Tx = 0\\\\
         &\Rightarrow& (x')^T \underbrace{(T')^TFT}_{F'} x = 0

成员变量
~~~~~~~~~~~~~~

1. 视角1下的特征点

   .. cpp:type:: Eigen::Vector2d FundamentalMatrixEightPointEstimator::X_t;

2. 视角2下的特征点

   .. cpp:type:: Eigen::Vector2d FundamentalMatrixEightPointEstimator::Y_t;

3. 基础矩阵

   .. cpp:type:: Eigen::Matrix3d FundamentalMatrixEightPointEstimator::M_t;

4. 估计模型所需的最少样本数

   .. cpp:member:: static const int FundamentalMatrixEightPointEstimator::kMinNumSamples = 8;


成员函数
~~~~~~~~~~~~~~

Estimate
^^^^^^^^^^^^

   从一组对应点估计基本矩阵

   .. cpp:function:: std::vector<FundamentalMatrixEightPointEstimator::M_t> FundamentalMatrixEightPointEstimator::Estimate(const std::vector<X_t>& points1, const std::vector<Y_t>& points2)

   .. code-block:: cpp

      std::vector<FundamentalMatrixEightPointEstimator::M_t>
      FundamentalMatrixEightPointEstimator::Estimate(
          const std::vector<X_t>& points1, const std::vector<Y_t>& points2) {
        CHECK_EQ(points1.size(), points2.size());

        // 对图像点进行居中和归一化以获得更好的数值稳定性
        std::vector<X_t> normed_points1;
        std::vector<Y_t> normed_points2;
        Eigen::Matrix3d points1_norm_matrix;
        Eigen::Matrix3d points2_norm_matrix;
        CenterAndNormalizeImagePoints(points1, &normed_points1, &points1_norm_matrix);
        CenterAndNormalizeImagePoints(points2, &normed_points2, &points2_norm_matrix);

        // 将齐次线性方程设置为 x2' * F * x1 = 0.
        Eigen::Matrix<double, Eigen::Dynamic, 9> cmatrix(points1.size(), 9);
        for (size_t i = 0; i < points1.size(); ++i) {
          cmatrix.block<1, 3>(i, 0) = normed_points1[i].homogeneous();
          cmatrix.block<1, 3>(i, 0) *= normed_points2[i].x();
          cmatrix.block<1, 3>(i, 3) = normed_points1[i].homogeneous();
          cmatrix.block<1, 3>(i, 3) *= normed_points2[i].y();
          cmatrix.block<1, 3>(i, 6) = normed_points1[i].homogeneous();
        }

        // 解约束矩阵的零空间
        Eigen::JacobiSVD<Eigen::Matrix<double, Eigen::Dynamic, 9>> cmatrix_svd(
            cmatrix, Eigen::ComputeFullV);
        const Eigen::VectorXd cmatrix_nullspace = cmatrix_svd.matrixV().col(8);
        const Eigen::Map<const Eigen::Matrix3d> ematrix_t(cmatrix_nullspace.data());

        // 强制执行以下两个约束：两个奇异值必须非零，一个奇异值必须为零
        Eigen::JacobiSVD<Eigen::Matrix3d> fmatrix_svd(
            ematrix_t.transpose(), Eigen::ComputeFullU | Eigen::ComputeFullV);
        Eigen::Vector3d singular_values = fmatrix_svd.singularValues();
        singular_values(2) = 0.0;
        const Eigen::Matrix3d F = fmatrix_svd.matrixU() *
                                  singular_values.asDiagonal() *
                                  fmatrix_svd.matrixV().transpose();

        const std::vector<M_t> models = {points2_norm_matrix.transpose() * F *
                                         points1_norm_matrix};
        return models;
      }



Residuals
^^^^^^^^^^^^^^^^

   计算一组对应点和给定基本矩阵的残差（使用SamponError）

   .. cpp:function:: void FundamentalMatrixEightPointEstimator::Residuals(const std::vector<X_t>& points1, const std::vector<Y_t>& points2,const M_t& E, std::vector<double>* residuals)

   .. code-block:: cpp

      void FundamentalMatrixEightPointEstimator::Residuals(
          const std::vector<X_t>& points1, const std::vector<Y_t>& points2,
          const M_t& E, std::vector<double>* residuals) {
        ComputeSquaredSampsonError(points1, points2, E, residuals);
      }