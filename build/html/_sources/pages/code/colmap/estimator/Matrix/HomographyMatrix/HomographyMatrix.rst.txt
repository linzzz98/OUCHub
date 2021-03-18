HomographyMatrix
===============================

直接线性变换算法以计算点对之间的单应性。 该算法从至少4个对应关系中计算出单应性的最小二乘估计。

单应性被定义为一个平面到另一个平面的投影映射。

单应性矩阵 :math:`H` 由两部分组成：相机内参  :math:`K = \left[\begin{matrix}f_x & 0 & c_x\\0 & f_y & c_y\\0 & 0 & 1\end{matrix}\right]` 和外参  :math:`W = [R~~~t]`

其中 :math:`R = [r_1~~~r_2~~~r_3]` ，即 :math:`H = KW`

单应性变换可以表示为：

.. math::

   \left[
   \begin{matrix}
   x_i'\\y_i'\\1
   \end{matrix}
   \right] = s
   \left[
   \begin{matrix}
   h_{11} & h_{12} & h_{13}\\h_{21} & h_{22} & h_{23}\\h_{31} & h_{32} & h_{33}
   \end{matrix}
   \right]
   \left[
   \begin{matrix}
   x_i\\y_i\\1
   \end{matrix}
   \right]

从而得到 |:point_down:| ：

.. math::

   \begin{eqnarray}
   x_i' &=& \frac{h_{11} x_i + h_{12} y_i + h_{13}}{h_{31}x_i + h_{32}y_i + h_{33}} \\
   y_i' &=& \frac{h_{21} x_i + h_{22} y_i + h_{23}}{h_{31}x_i + h_{32}y_i + h_{33}}
   \end{eqnarray}

进一步变换为 |:point_down:| ：

.. math::

   x_ih_{11} + y_i h_{12} + h_{13} - x_i'x_ih_{31} - x_i'y_ih_{32} - x_i'h_{33} = 0\\\\
   x_ih_{21} + y_i h_{22} + h_{23} - y_i'x_ih_{31} - y_i'y_ih_{32} - y_i'h_{33} = 0

有4对已知的对应点 :math:`(x_i,y_i)` 和  :math:`(x_i',y_i')` 那么有：

.. math::

   \begin{eqnarray}
   A =
   \left[
   \begin{matrix}
   x_1 & y_1 & 1 & 0 & 0 & 0 & -x_1'x_1 & -x_1'y_1 & -x_1'\\
   0 & 0 & 0 & x_1 & y_1 & 1 & -y_1'x_1 & -y_1'y_1 & -y_1'\\
   x_2 & y_2 & 1 & 0 & 0 & 0 & -x_2'x_2 & -x_2'y_2 & -x_2'\\
   0 & 0 & 0 & x_2 & y_2 & 1 & -y_2'x_2 & -y_2'y_ 2 & -y_2 '\\
   x_3 & y_3 & 1 & 0 & 0 & 0 & -x_3'x_3 & -x_3'y_3 & -x_3'\\
   0 & 0 & 0 & x_3 & y_3 & 1 & -y_3'x_3 & -y_3'y_3 & -y_3'\\
   x_4 & y_4 & 1 & 0 & 0 & 0 & -x_4'x_4 & -x_4'y_4 & -x_4'\\
   0 & 0 & 0 & x_4 & y_4 & 1 & -y_4'x_4 & -y_4'y_4 & -y_4'\\
   \end{matrix}
   \right]\\\\
   h =
   \left[
   \begin{matrix}
   h_{11} & h_{12} & h_{13} & h_{21} & h_{22} & h_{23} & h_{31} & h_{32} & h_{33}
   \end{matrix}
   \right]^T
   \end{eqnarray}

从而有：

.. math::

   Ah = 0

.. note::

   矩阵 :math:`A` 也可以写作：

   .. math::

      \left[
      \begin{matrix}
      x_1 & y_1 & 1 & 0 & 0 & 0 & -x_1'x_1 & -x_1'y_1 & -x_1'\\
      x_2 & y_2 & 1 & 0 & 0 & 0 & -x_2'x_2 & -x_2'y_2 & -x_2'\\
      x_3 & y_3 & 1 & 0 & 0 & 0 & -x_3'x_3 & -x_3'y_3 & -x_3'\\
      x_4 & y_4 & 1 & 0 & 0 & 0 & -x_4'x_4 & -x_4'y_4 & -x_4'\\
      0 & 0 & 0 & x_1 & y_1 & 1 & -y_1'x_1 & -y_1'y_1 & -y_1'\\
      0 & 0 & 0 & x_2 & y_2 & 1 & -y_2'x_2 & -y_2'y_ 2 & -y_2 '\\
      0 & 0 & 0 & x_3 & y_3 & 1 & -y_3'x_3 & -y_3'y_3 & -y_3'\\
      0 & 0 & 0 & x_4 & y_4 & 1 & -y_4'x_4 & -y_4'y_4 & -y_4'\\
      \end{matrix}
      \right]

   不影响最终计算 :math:`h` 的结果

.. note::

   单应矩阵中自由度是8， :math:`h_{33}` = 1，所以在编程时可以将等式中 :math:`A` 矩阵的最后一列舍去。


:求解过程:

1. 计算 :math:`|\lambda I - A^HA| = 0` 的解，由于 :math:`A` 是一个 :math:`8 \times 9` 且秩为8的矩阵，所以得到的解 :math:`\lambda` 会有8个非0解和一个0解，将 :math:`\lambda` 从大到小排列为 :math:`\lambda_i(i = 1,2,3,...,9)`，称 :math:`\lambda_i` 为 :math:`A^HA` 的特征值。

2. 对于 :math:`\lambda_i(i = 1,2,3,...,9)`，求出来对应 :math:`A` 的奇异值 :math:`\sigma_i(i = 1,2,3,...,9)` 以及 :math:`A^HA` 的特征向量 :math:`\alpha_i(i=1,2,3,...,9)`。

3. 取 :math:`\lambda_9` 所对应的特征向量，即为 :math:`h` 的一个非零解。

.. important::

   总结为：对 :math:`A` 进行SVD分解，然后取 :math:`V` 矩阵的最后一列，即为 :math:`h` 的一个非零解


成员变量
-------------------------

1. 视角1下的特征点

   .. cpp:type:: Eigen::Vector2d HomographyMatrixEstimator::X_t;

2. 视角2下的特征点

    .. cpp:type:: Eigen::Vector2d HomographyMatrixEstimator::Y_t;

3. 基础矩阵

    .. cpp:type:: Eigen::Matrix3d HomographyMatrixEstimator::M_t;

4. 估计模型所需的最少样本数

    .. cpp:member:: static const int HomographyMatrixEstimator::kMinNumSamples = 4;


成员函数
------------------------

1. **Estimate**

使用至少四个点估计单应性矩阵

.. cpp:function:: std::vector<HomographyMatrixEstimator::M_t> HomographyMatrixEstimator::Estimate(const std::vector<X_t>& points1, const std::vector<Y_t>& points2)

.. code-block:: cpp

   std::vector<HomographyMatrixEstimator::M_t> HomographyMatrixEstimator::Estimate(
       const std::vector<X_t>& points1, const std::vector<Y_t>& points2) {
     CHECK_EQ(points1.size(), points2.size());

     const size_t N = points1.size();

     // 对图像点进行居中和归一化以获得更好的数值稳定性
     std::vector<X_t> normed_points1;
     std::vector<Y_t> normed_points2;
     Eigen::Matrix3d points1_norm_matrix;
     Eigen::Matrix3d points2_norm_matrix;
     CenterAndNormalizeImagePoints(points1, &normed_points1, &points1_norm_matrix);
     CenterAndNormalizeImagePoints(points2, &normed_points2, &points2_norm_matrix);

     // 设置约束矩阵
     Eigen::Matrix<double, Eigen::Dynamic, 9> A = Eigen::MatrixXd::Zero(2 * N, 9);

     for (size_t i = 0, j = N; i < points1.size(); ++i, ++j) {
       const double s_0 = normed_points1[i](0);
       const double s_1 = normed_points1[i](1);
       const double d_0 = normed_points2[i](0);
       const double d_1 = normed_points2[i](1);

       A(i, 0) = -s_0;
       A(i, 1) = -s_1;
       A(i, 2) = -1;
       A(i, 6) = s_0 * d_0;
       A(i, 7) = s_1 * d_0;
       A(i, 8) = d_0;

       A(j, 3) = -s_0;
       A(j, 4) = -s_1;
       A(j, 5) = -1;
       A(j, 6) = s_0 * d_1;
       A(j, 7) = s_1 * d_1;
       A(j, 8) = d_1;
     }

     // 求解约束矩阵的零空间
     Eigen::JacobiSVD<Eigen::Matrix<double, Eigen::Dynamic, 9>> svd(A, Eigen::ComputeFullV);

     const Eigen::VectorXd nullspace = svd.matrixV().col(8);
     Eigen::Map<const Eigen::Matrix3d> H_t(nullspace.data());

     const std::vector<M_t> models = {points2_norm_matrix.inverse() *
                                      H_t.transpose() * points1_norm_matrix};
     return models;
   }