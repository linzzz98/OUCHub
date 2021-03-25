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

      const double np_0 = M_00 * p_0 + M_01 * p_1 + M_02;   //np_0 = nf(x-cx)
      const double np_1 = M_10 * p_0 + M_11 * p_1 + M_12;   //np_1 = nf(y-cy)
      const double np_2 = M_20 * p_0 + M_21 * p_1 + M_22;   //np_2 = 1

      const double inv_np_2 = 1.0 / np_2;                   //inv_np_2 = 1
      (*normed_points)[i](0) = np_0 * inv_np_2;             //normed_points = (nf(x-cx),nf(y-cy))
      (*normed_points)[i](1) = np_1 * inv_np_2;
    }

.. note::

   1. 定义并计算质心 :math:`c`

      .. code-block:: cpp

         Eigen::Vector2d centroid(0, 0);

         for (const auto point : points){
            centroid += point; }

         centroid /= points.size();

   2. 求质心的均方根误差

      :计算 ``点到质心距离的平方范数``:

         .. code-block:: cpp

            double rms_mean_dist = 0;

            for (const auto point : points) {
              rms_mean_dist += (point - centroid).squaredNorm();
            }

      :计算 ``各点质心均方根误差``:

         .. code-block:: cpp

            rms_mean_dist = std::sqrt(rms_mean_dist / points.size());

   3. 构建归一化矩阵

      .. math::
         nf = \frac{\sqrt{2}}{rms\_mean\_dist},~~~c_x = centroid(0),~~~c_y = centroid(1)\\\\

      .. math::
         matrix = \left[
         \begin{matrix}
         nf & 0 & -nf*c_x\\
         0 & nf & -nf*c_y\\
         0 & 0 & 1
         \end{matrix}
         \right]

   4. 应用归一化矩阵

      * :math:`{np}_0 = nf(x-c_x) = \frac{\sqrt{2} (x-c_x)}{rms\_mean\_dist}`

         .. code-block:: cpp

            const double np_0 = M_00 * p_0 + M_01 * p_1 + M_02;

      * :math:`{np}_1 = nf(y-c_y) = \frac{\sqrt{2} (y-c_y)}{rms\_mean\_dist}`

         .. code-block:: cpp

            const double np_1 = M_10 * p_0 + M_11 * p_1 + M_12;

      * :math:`{np}_2 = 1`

         .. code-block:: cpp

            const double np_2 = M_20 * p_0 + M_21 * p_1 + M_22;

      * :math:`{inv\_np_2} = 1`

         .. code-block:: cpp

            const double inv_np_2 = 1.0 / np_2;

      * :math:`normed\_points = (nf(x-c_x),nf(y-c_y)) = \sqrt{2}(\frac{(x-c_x)}{rms\_mean\_dist},\frac{(y-c_y)}{rms\_mean\_dist})`

         .. code-block:: cpp

            (*normed_points)[i](0) = np_0 * inv_np_2;

            (*normed_points)[i](1) = np_1 * inv_np_2;

ComputeSquaredSampsonError
-----------------------------

计算一组对应点和给定的基本矩阵或基本矩阵的残差。

**残差定义为Sampson误差的平方。**

.. math::


   || \epsilon||^2 = \frac{(x_2^TEx_1)^2}{(Ex_1)_1^2 + (Ex_1)_2^2 + (E^Tx_2)_1^2 + (E^Tx_2)_2^2}

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

给定一组2D-3D点对应关系和一个投影矩阵，计算平方重投影误差。

.. math::

   P = \left[
   \begin{matrix}
   R & t\\0 & 1
   \end{matrix}
   \right]

.. code-block:: cpp

   void ComputeSquaredReprojectionError(
       const std::vector<Eigen::Vector2d>& points2D,
       const std::vector<Eigen::Vector3d>& points3D,
       const Eigen::Matrix3x4d& proj_matrix, std::vector<double>* residuals) {
     CHECK_EQ(points2D.size(), points3D.size());

     residuals->resize(points2D.size());

     const double P_00 = proj_matrix(0, 0);
     const double P_01 = proj_matrix(0, 1);
     const double P_02 = proj_matrix(0, 2);
     const double P_03 = proj_matrix(0, 3);
     const double P_10 = proj_matrix(1, 0);
     const double P_11 = proj_matrix(1, 1);
     const double P_12 = proj_matrix(1, 2);
     const double P_13 = proj_matrix(1, 3);
     const double P_20 = proj_matrix(2, 0);
     const double P_21 = proj_matrix(2, 1);
     const double P_22 = proj_matrix(2, 2);
     const double P_23 = proj_matrix(2, 3);

     for (size_t i = 0; i < points2D.size(); ++i) {
       const double X_0 = points3D[i](0);
       const double X_1 = points3D[i](1);
       const double X_2 = points3D[i](2);

       // 将3D点从世界坐标系投影到相机坐标系
       const double px_2 = P_20 * X_0 + P_21 * X_1 + P_22 * X_2 + P_23;

       // 检查3D点是否在相机前面
       if (px_2 > std::numeric_limits<double>::epsilon()) {
         const double px_0 = P_00 * X_0 + P_01 * X_1 + P_02 * X_2 + P_03;
         const double px_1 = P_10 * X_0 + P_11 * X_1 + P_12 * X_2 + P_13;

         const double x_0 = points2D[i](0);
         const double x_1 = points2D[i](1);

         const double inv_px_2 = 1.0 / px_2;
         const double dx_0 = x_0 - px_0 * inv_px_2;
         const double dx_1 = x_1 - px_1 * inv_px_2;

         (*residuals)[i] = dx_0 * dx_0 + dx_1 * dx_1;
       } else {
         (*residuals)[i] = std::numeric_limits<double>::max();
       }
     }
   }

.. note::

   1. 投影3d点的 :math:`z` 坐标（世界坐标系——相机坐标系）

      .. code-block:: cpp

         const double px_2 = P_20 * X_0 + P_21 * X_1 + P_22 * X_2 + P_23;

   2. 判断 :math:`z` 是否相机前面（ :math:`z > 0`）

      .. code-block:: cpp

         if (px_2 > std::numeric_limits<double>::epsilon())

   3. 如果 :math:`z` 在相机前，则计算重投影误差平方

      :投影3d点的x坐标:

         .. code-block:: cpp

            const double px_0 = P_00 * X_0 + P_01 * X_1 + P_02 * X_2 + P_03;

      :投影3d点的y坐标:

         .. code-block:: cpp

            const double px_1 = P_10 * X_0 + P_11 * X_1 + P_12 * X_2 + P_13;

      :计算2d点到投影点距离:

         .. code-block:: cpp

            const double inv_px_2 = 1.0 / px_2;
            const double dx_0 = x_0 - px_0 * inv_px_2;
            const double dx_1 = x_1 - px_1 * inv_px_2;

      :计算平方重投影误差:

         .. code-block:: cpp

            (*residuals)[i] = dx_0 * dx_0 + dx_1 * dx_1;