.. default-domain:: cpp

Utils
==========


CenterAndNormalizeImagePoints
-------------------------------

将图像点居中并归一化。

这些点以两步过程进行变换，该过程表示为变换矩阵。
所得点的矩阵通常比原始点的矩阵条件更好。

1. 使图像点居中，以使新坐标系的原点位于图像点的质心处。
2. 标准化图像点，以使这些点到坐标系的平均距离为\ :math:`\sqrt{2}`\ 。

-  @param points Image coordinates.

-  @param normed\_points Transformed image coordinates.

-  @param matrix 3x3 transformation matrix.

.. cpp:function:: void CenterAndNormalizeImagePoints(const std::vector& points, std::vector* normed_points, Eigen::Matrix3d* matrix)

.. code-block:: cpp

    // 计算质心λ
    Eigen::Vector2d centroid(0, 0);

    for (const auto point : points){
        centroid += point; }

    centroid /= points.size();

    // 各点质心均方根误差
    double rms_mean_dist = 0;
    for (const auto point : points) {
      // l2范数的平方
      rms_mean_dist += (point - centroid).squaredNorm();
    }

    rms_mean_dist = std::sqrt(rms_mean_dist / points.size());

    // 组成归一化矩阵
    const double norm_factor = std::sqrt(2.0) / rms_mean_dist;
    *matrix << norm_factor, 0, -norm_factor * centroid(0), 0, norm_factor,
        -norm_factor * centroid(1), 0, 0, 1;

    // 应用归一化矩阵
    normed_points->resize(points.size());

    const double M_00 = (*matrix)(0, 0);
    const double M_01 = (*matrix)(0, 1);
    const double M_02 = (*matrix)(0, 2);
    const double M_10 = (*matrix)(1, 0);
    const double M_11 = (*matrix)(1, 1);
    const double M_12 = (*matrix)(1, 2);
    const double M_20 = (*matrix)(2, 0);
    const double M_21 = (*matrix)(2, 1);
    const double M_22 = (*matrix)(2, 2);

    for (size_t i = 0; i < points.size(); ++i) {
      const double p_0 = points[i](0);
      const double p_1 = points[i](1);

      const double np_0 = M_00 * p_0 + M_01 * p_1 + M_02;   //np_0 = λ(x-x0)
      const double np_1 = M_10 * p_0 + M_11 * p_1 + M_12;   //np_1 = λ(y-y0)
      const double np_2 = M_20 * p_0 + M_21 * p_1 + M_22;   //np_2 = 1

      const double inv_np_2 = 1.0 / np_2;                   //inv_np_2 = 1
      (*normed_points)[i](0) = np_0 * inv_np_2;             //normed_points = (λ(x-x0),λ(y-y0))
      (*normed_points)[i](1) = np_1 * inv_np_2;
    }

ComputeSquaredSampsonError
-----------------------------

计算一组对应点和给定的基本矩阵或基本矩阵的残差。

**残差定义为Sampson误差的平方。**

.. math::


   || \epsilon||^2 = \frac{(x_2^TEx_1)^2}{(Ex_1)_1^2 + (Ex_1)_2^2 + (E^Tx_2)_1^2 + (E^Tx_2)_2^2}

-  @param points1 First set of corresponding points as Nx2 matrix.
-  @param points2 Second set of corresponding points as Nx2 matrix.
-  @param E 3x3 fundamental or essential matrix.
-  @param residuals Output vector of residuals.

.. cpp:function:: void ComputeSquaredSampsonError(const std::vector& points1, const std::vector& points2, const Eigen::Matrix3d& E, std::vector* residuals)

.. code-block:: cpp

    CHECK_EQ(points1.size(), points2.size());

    residuals->resize(points1.size());

    // 此代码可能不如本征表达式好，但是速度明显更快

    const double E_00 = E(0, 0);
    const double E_01 = E(0, 1);
    const double E_02 = E(0, 2);
    const double E_10 = E(1, 0);
    const double E_11 = E(1, 1);
    const double E_12 = E(1, 2);
    const double E_20 = E(2, 0);
    const double E_21 = E(2, 1);
    const double E_22 = E(2, 2);

    for (size_t i = 0; i < points1.size(); ++i) {
    const double x1_0 = points1[i](0);
    const double x1_1 = points1[i](1);
    const double x2_0 = points2[i](0);
    const double x2_1 = points2[i](1);

    // Ex1 = E * points1[i].homogeneous();
    const double Ex1_0 = E_00 * x1_0 + E_01 * x1_1 + E_02;
    const double Ex1_1 = E_10 * x1_0 + E_11 * x1_1 + E_12;
    const double Ex1_2 = E_20 * x1_0 + E_21 * x1_1 + E_22;

    // Etx2 = E.transpose() * points2[i].homogeneous();
    const double Etx2_0 = E_00 * x2_0 + E_10 * x2_1 + E_20;
    const double Etx2_1 = E_01 * x2_0 + E_11 * x2_1 + E_21;

    // x2tEx1 = points2[i].homogeneous().transpose() * Ex1;
    const double x2tEx1 = x2_0 * Ex1_0 + x2_1 * Ex1_1 + Ex1_2;

    // Sampson distance
    (*residuals)[i] =
        x2tEx1 * x2tEx1 /
        (Ex1_0 * Ex1_0 + Ex1_1 * Ex1_1 + Etx2_0 * Etx2_0 + Etx2_1 * Etx2_1);
    }


ComputeSquaredReprojectionError
----------------------------------

