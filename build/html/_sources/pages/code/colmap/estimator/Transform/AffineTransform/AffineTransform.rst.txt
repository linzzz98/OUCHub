AffineTransform
=============================

非齐次坐标的仿射变换：

.. math::

   \left[
   \begin{matrix}
   \tilde{x}\\ \tilde{y}
   \end{matrix}
   \right]=
   \left[
   \begin{matrix}
   a_{11} & a_{12} \\a_{21} & a_{22}
   \end{matrix}
   \right]
   \left[
   \begin{matrix}
   x\\y
   \end{matrix}
   \right]+
   \left[
   \begin{matrix}
   a_{13}\\a_{23}
   \end{matrix}
   \right]

齐次坐标的仿射变换：

.. math::

   \left[
   \begin{matrix}
   \tilde{x}\\ \tilde{y}\\ 1
   \end{matrix}
   \right] = A
   \left[
   \begin{matrix}
   x\\y\\1
   \end{matrix}
   \right]

仿射变换矩阵：

.. math::

   A = \left[
   \begin{matrix}
   a_{11} & a_{12} & a_{13}\\a_{21}  & a_{22} & a_{23}\\0 & 0 & 1
   \end{matrix}
   \right]

齐次坐标的平移变换过程：

.. math::

   \left[
   \begin{matrix}
   \tilde{x}\\ \tilde{y}\\ 1
   \end{matrix}
   \right] =
   \left[
   \begin{matrix}
   1 & 0 & \Delta x\\ 0 & 1 & \Delta y \\ 0 & 0 & 1
   \end{matrix}
   \right]
   \left[
   \begin{matrix}
   x\\y\\1
   \end{matrix}
   \right]

.. note::

   :math:`\Delta x > 0` 表示沿 :math:`x` 轴正方向移动，    :math:`\Delta x < 0` 表示沿 :math:`x` 轴负方向移动

   :math:`\Delta y > 0` 表示沿 :math:`y` 轴正方向移动，    :math:`\Delta y < 0` 表示沿 :math:`y` 轴负方向移动

齐次坐标的缩放变换过程：

   .. math::

      \left[
      \begin{matrix}
      \tilde{x}\\ \tilde{y}\\ 1
      \end{matrix}
      \right] =
      \left[
      \begin{matrix}
      S_x & 0 & 0\\ 0 & S_y & 0 \\ 0 & 0 & 1
      \end{matrix}
      \right]
      \left[
      \begin{matrix}
      x\\y\\1
      \end{matrix}
      \right]

.. note::

   若 :math:`S_x > 1` 表示沿着水平方向放大， :math:`0 < S_x < 1` 表示沿着水平方向缩小

   若 :math:`S_y > 1` 表示沿着垂直方向放大， :math:`0 < S_y < 1` 表示沿着垂直方向缩小

   若  :math:`S_x = S_y` 则表示等比例缩放

齐次坐标的旋转变换过程：

   .. math::

      \left[
      \begin{matrix}
      \tilde{x}\\ \tilde{y}\\ 1
      \end{matrix}
      \right] =
      \left[
      \begin{matrix}
      cos\theta & -sin\theta & 0 \\ sin\theta & cos\theta & 0 \\ 0 & 0 & 1
      \end{matrix}
      \right]
      \left[
      \begin{matrix}
      x\\y\\1
      \end{matrix}
      \right]

成员变量
-------------------------

1. 2D图像特征点

   .. cpp:type:: Eigen::Vector2d AffineTransformEstimator::X_t;

2. 2D图像仿射变换后的特征点

    .. cpp:type:: Eigen::Vector2d AffineTransformEstimator::Y_t;

3. 仿射变换矩阵

    .. cpp:type:: Eigen::Matrix<double, 2, 3> AffineTransformEstimator::M_t;

4. 估计模型所需的最少样本数

    .. cpp:member:: static const int AffineTransformEstimator::kMinNumSamples = 3;

成员函数
---------------------

1. **Estimate**

.. cpp:function:: static std::vector<M_t> AffineTransformEstimator::Estimate(const std::vector<X_t>& points1, const std::vector<Y_t>& points2);

.. code-block:: cpp

   std::vector<AffineTransformEstimator::M_t> AffineTransformEstimator::Estimate(
       const std::vector<X_t>& points1, const std::vector<Y_t>& points2) {
     CHECK_EQ(points1.size(), points2.size());
     CHECK_GE(points1.size(), 3);

     // 设置要求解的线性系统，以获得仿射变换的最小二乘解。
     Eigen::MatrixXd C(2 * points1.size(), 6);
     C.setZero();
     Eigen::VectorXd b(2 * points1.size(), 1);

     for (size_t i = 0; i < points1.size(); ++i) {
       const Eigen::Vector2d& x1 = points1[i];
       const Eigen::Vector2d& x2 = points2[i];

       C(2 * i, 0) = x1(0);
       C(2 * i, 1) = x1(1);
       C(2 * i, 2) = 1.0f;
       b(2 * i) = x2(0);

       C(2 * i + 1, 3) = x1(0);
       C(2 * i + 1, 4) = x1(1);
       C(2 * i + 1, 5) = 1.0f;
       b(2 * i + 1) = x2(1);
     }

     const Eigen::VectorXd nullspace =
         C.jacobiSvd(Eigen::ComputeThinU | Eigen::ComputeThinV).solve(b);

     Eigen::Map<const Eigen::Matrix<double, 3, 2>> A_t(nullspace.data());

     const std::vector<M_t> models = {A_t.transpose()};
     return models;
   }

.. note::
   使用最小二乘解来求解仿射变换矩阵

   分别设起始和结束矩阵的坐标为 :math:`(a_x,a_y),(b_x,b_y),(c_x,c_y)` ，变换后为 :math:`(a_x',a_y'),(b_x',b_y'),(c_x',c_y')`

   新坐标的 :math:`X` 值，是需要原坐标的 :math:`(x,y)` 值参与过来进行变化的（乘以合适的系数），然后还要加上偏移的系数。

   变换方程为 :math:`a_x' = a_x m_{00} + a_y m_{01} + m_{02}`

   根据矩阵特征，补充一列1，构造矩阵：

   .. math::

      \left[
      \begin{matrix}
      a_x & a_y & 1\\b_x & b_y & 1\\c_x & c_y & 1
      \end{matrix}
      \right]
      \left[
      \begin{matrix}
      m_{00}\\m_{01}\\m_{02}
      \end{matrix}
      \right]
      \left[
      \begin{matrix}
      a_x'\\b_x'\\c_x'
      \end{matrix}
      \right]

   这只是变换了 :math:`a_x,b_x,c_x` ，其实也可以认为变换了 :math:`y` （原理一样，系数不同）。

   要求另一半，根据坐标相乘的原理，只能把前三列置零，再把后三列复制进去（仿射矩阵变为 :math:`6\times 1` ），其实就是上面矩阵乘法的重复，只不过交错一下形成 :math:`x,y` 交错的排列：

   .. math::

      \left[
      \begin{matrix}
      a_x & a_y & 1 & 0 & 0 & 0\\0 & 0 & 0 & a_x & a_y & 1\\b_x & b_y & 1 & 0 & 0 & 0\\0 & 0 & 0 & b_x & b_y & 1\\c_x & c_y & 1 & 0 & 0 & 0\\0 & 0 & 0 & c_x & c_y & 1
      \end{matrix}
      \right]
      \left[
      \begin{matrix}
      m_{00}\\m_{01}\\m_{02}\\m_{10}\\m_{11}\\m_{12}
      \end{matrix}
      \right]
      \left[
      \begin{matrix}
      a_x'\\a_y'\\b_x'\\b_y'\\c_x'\\c_y'
      \end{matrix}
      \right]

   .. code-block:: cpp

     Eigen::MatrixXd C(2 * points1.size(), 6);
     C.setZero();
     Eigen::VectorXd b(2 * points1.size(), 1);

     for (size_t i = 0; i < points1.size(); ++i) {
       const Eigen::Vector2d& x1 = points1[i];
       const Eigen::Vector2d& x2 = points2[i];

       C(2 * i, 0) = x1(0);
       C(2 * i, 1) = x1(1);
       C(2 * i, 2) = 1.0f;
       b(2 * i) = x2(0);

       C(2 * i + 1, 3) = x1(0);
       C(2 * i + 1, 4) = x1(1);
       C(2 * i + 1, 5) = 1.0f;
       b(2 * i + 1) = x2(1);
     }

   接下来通过SVD奇异值分解，求解零空间，也就是 :math:`m_{00} ———— m_{12}`

   .. code-block:: cpp

      const Eigen::VectorXd nullspace = C.jacobiSvd(Eigen::ComputeThinU | Eigen::ComputeThinV).solve(b);

   最后将其变为 :math:`3\times 2` 维矩阵 :math:`A_t` ，最后求转置即维仿射变换矩阵 :math:`2\times 3`


2. **Residuals**

.. cpp:function:: void AffineTransformEstimator::Residuals(const std::vector<X_t>& points1, const std::vector<Y_t>& points2, const M_t& A, std::vector<double>* residuals)

.. code-block:: cpp

   void AffineTransformEstimator::Residuals(const std::vector<X_t>& points1,
                                         const std::vector<Y_t>& points2,
                                         const M_t& A,
                                         std::vector<double>* residuals) {
     CHECK_EQ(points1.size(), points2.size());

     residuals->resize(points1.size());

     // 请注意，此代码的表达可能不如Eigenb，但在各种测试中却明显更快

     const double A_00 = A(0, 0);
     const double A_01 = A(0, 1);
     const double A_02 = A(0, 2);
     const double A_10 = A(1, 0);
     const double A_11 = A(1, 1);
     const double A_12 = A(1, 2);

     for (size_t i = 0; i < points1.size(); ++i) {
       const double s_0 = points1[i](0);
       const double s_1 = points1[i](1);
       const double d_0 = points2[i](0);
       const double d_1 = points2[i](1);

       const double pd_0 = A_00 * s_0 + A_01 * s_1 + A_02;
       const double pd_1 = A_10 * s_0 + A_11 * s_1 + A_12;

       const double dd_0 = d_0 - pd_0;
       const double dd_1 = d_1 - pd_1;

       (*residuals)[i] = dd_0 * dd_0 + dd_1 * dd_1;
     }
   }

.. note::

   :math:`dd_0`  = 变换后的理想坐标 :math:`\tilde{x}` - 通过仿射变换变换的实际坐标 :math:`x'`

   :math:`dd_1`  = 变换后的理想坐标 :math:`\tilde{x}` - 通过仿射变换变换的实际坐标 :math:`y'`

   :math:`residuals` =  :math:`{dd_0}^2 + {dd_1}^2`