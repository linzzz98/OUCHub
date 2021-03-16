.. default-domain:: cpp

Matrix
======

Essential Matrix
----------------

将基本矩阵分解为可能的旋转和平移。

DecomposeEssentialMatrix
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

假定第一个位姿为\ :math:`P = [I | 0]`\ 和其他四个可能的第二个姿势的集合定义为：\ :math:`\{[R_1 | t],[R_2 | t],    [R_1 | -t],[R_2 | -t]\}`

-  @param E 3x3 essential matrix.
-  @param R1 First possible 3x3 rotation matrix.
-  @param R2 Second possible 3x3 rotation matrix.
-  @param t 3x1 possible translation vector (also -t possible).

.. cpp:function:: void DecomposeEssentialMatrix(const Eigen::Matrix3d& E, Eigen::Matrix3d* R1, Eigen::Matrix3d* R2, Eigen::Vector3d* t)

.. code-block:: cpp

    void DecomposeEssentialMatrix(const Eigen::Matrix3d& E, Eigen::Matrix3d* R1,
                                  Eigen::Matrix3d* R2, Eigen::Vector3d* t) {
      Eigen::JacobiSVD<Eigen::Matrix3d> svd(
          E, Eigen::ComputeFullU | Eigen::ComputeFullV);
      Eigen::Matrix3d U = svd.matrixU();
      Eigen::Matrix3d V = svd.matrixV().transpose();

      if (U.determinant() < 0) {
        U *= -1;
      }
      if (V.determinant() < 0) {
        V *= -1;
      }

      Eigen::Matrix3d W;
      W << 0, 1, 0, -1, 0, 0, 0, 0, 1;

      *R1 = U * W * V;
      *R2 = U * W.transpose() * V;
      *t = U.col(2).normalized();
    }

.. note::

    具体证明如下：正交矩阵\ :math:`W`\ ：\ :math:`\left[\begin{matrix}0 & -1 & 0\\1 & 0 & 0\\0 & 0 & 1\end{matrix}\right]`
    反对称矩阵\ :math:`Z`\ ：\ :math:`\left[\begin{matrix}0 & -1 & 0\\1 & 0 & 0\\0 & 0 & 0\end{matrix}\right]`

    由\ :math:`E = t^∧R =  SR`\ ，其中\ :math:`S`\ 是反对称矩阵。

    根据定义：

    .. math::

       S=kUZU^T

    其中，\ :math:`U`\ 是正交矩阵，\ :math:`Z = diag(1,1,0)W`

    得到：

    .. math::

       S = kUdiag(1,1,0)WU^T

    即：

    .. math::

       E = Udiag(1,1,0)WU^TR

    由SVD分解可得：

    .. math::

       WU^TR = V^T

    由于\ :math:`E`\ 和\ :math:`-E`\ 等价则有两种可能：

    .. math::

      \begin{eqnarray}
      R &=& UW^TV^T\\
      R &=& U(-W^T)V^T = UWV^T
      \end{eqnarray}


    :math:`t^∧ = S`\ ，忽略\ :math:`k`\ ，化简后得到\ :math:`t = U.col(2)`\ （U的最后一列）

    找到特征点在两个相机位姿下的深度均为正的解。


PoseFromEssentialMatrix
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

从给定的基本矩阵中恢复最可能的位姿。

假设第一张图片的姿态为\ :math:`P = [I | 0]`

-  @param E 3x3 essential matrix.
-  @param points1 First set of corresponding points.
-  @param points2 Second set of corresponding points.
-  @param R Most probable 3x3 rotation matrix.
-  @param t Most probable 3x1 translation vector.
-  @param points3D Triangulated 3D points infront of camera.

.. cpp:function:: void PoseFromEssentialMatrix(const Eigen::Matrix3d& E, const std::vector<Eigen::Vector2d>& points1, const std::vector<Eigen::Vector2d>& points2, Eigen::Matrix3d* R, Eigen::Vector3d* t, std::vector<Eigen::Vector3d>* points3D)

.. code-block:: cpp

    void PoseFromEssentialMatrix(const Eigen::Matrix3d& E,
                                 const std::vector<Eigen::Vector2d>& points1,
                                 const std::vector<Eigen::Vector2d>& points2,
                                 Eigen::Matrix3d* R, Eigen::Vector3d* t,
                                 std::vector<Eigen::Vector3d>* points3D) {
      CHECK_EQ(points1.size(), points2.size());

      Eigen::Matrix3d R1;
      Eigen::Matrix3d R2;
      DecomposeEssentialMatrix(E, &R1, &R2, t);

      // 得到所有由E分解出的位姿组合
      const std::array<Eigen::Matrix3d, 4> R_cmbs{{R1, R2, R1, R2}};
      const std::array<Eigen::Vector3d, 4> t_cmbs{{*t, *t, -*t, -*t}};

      points3D->clear();

      for (size_t i = 0; i < R_cmbs.size(); ++i) {

        std::vector<Eigen::Vector3d> points3D_cmb;

        // 进行cheirality约束测试，即确定哪个三角对应关系位于两个摄像机的前面。
        // -- 该函数在pose.h中 -- //
        CheckCheirality(R_cmbs[i], t_cmbs[i], points1, points2, &points3D_cmb);

        if (points3D_cmb.size() >= points3D->size()) {
          *R = R_cmbs[i];
          *t = t_cmbs[i];
          *points3D = points3D_cmb;
        }
      }
    }


EssentialMatrixFromPose
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

根据相对的相机位姿构成基本矩阵

假设第一个摄像机姿态具有投影矩阵\ :math:`P = [I | 0]`\ ，第二个摄影机的姿态作为从世界到摄影机系统的转换而给出。

-  @param R 3x3 rotation matrix.

-  @param t 3x1 translation vector.

-  @return 3x3 essential matrix.

.. cpp:function:: Eigen::Matrix3d EssentialMatrixFromPose(const Eigen::Matrix3d& R, const Eigen::Vector3d& t)

.. code-block:: cpp

    Eigen::Matrix3d EssentialMatrixFromPose(const Eigen::Matrix3d& R,
                                            const Eigen::Vector3d& t) {
      return CrossProductMatrix(t.normalized()) * R;
    }

    Eigen::Matrix3d CrossProductMatrix(const Eigen::Vector3d& vector) {

      Eigen::Matrix3d matrix;

      matrix << 0, -vector(2), vector(1), vector(2), 0, -vector(0), -vector(1),
          vector(0), 0;

      return matrix;
    }

.. note::

    证明：\ :math:`E = t^∧R = \left[\begin{matrix}0 & -t_z & t_y\\t_z & 0 & -t_x \\-t_y & t_x & 0\end{matrix}\right]R`


EssentialMatrixFromAbsolutePoses
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

从两个绝对相机姿势构成基本矩阵

-  @param proj\_matrix1 3x4 projection matrix.

-  @param proj\_matrix2 3x4 projection matrix.

-  @return 3x3 essential matrix.

.. cpp:function:: Eigen::Matrix3d EssentialMatrixFromAbsolutePoses(const Eigen::Matrix3x4d& proj_matrix1, const Eigen::Matrix3x4d& proj_matrix2)

.. code-block:: cpp

    Eigen::Matrix3d EssentialMatrixFromAbsolutePoses(
        const Eigen::Matrix3x4d& proj_matrix1,
        const Eigen::Matrix3x4d& proj_matrix2) {

      const Eigen::Matrix3d R1 = proj_matrix1.leftCols<3>();
      const Eigen::Matrix3d R2 = proj_matrix2.leftCols<3>();
      const Eigen::Vector3d t1 = proj_matrix1.rightCols<1>();
      const Eigen::Vector3d t2 = proj_matrix2.rightCols<1>();

      // Relative transformation between to cameras.
      const Eigen::Matrix3d R = R2 * R1.transpose();
      const Eigen::Vector3d t = t2 - R * t1;

      return EssentialMatrixFromPose(R, t);
    }


FindOptimalImageObservations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

查找最佳图像点，例如：
:math:`optimal\_point1^T * E * optimal\_point2 = 0`

《Lindstrom, P., "Triangulation made easy",Computer Vision and Pattern
Recognition (CVPR),2010 IEEE Conference on , vol., no., pp.1554,1561,
13-18 June 2010》

-  @param E Essential or fundamental matrix.
-  @param point1 Corresponding 2D point in first image.
-  @param point2 Corresponding 2D point in second image.
-  @param optimal\_point1 Estimated optimal image point in the first
   image.
-  @param optimal\_point2 Estimated optimal image point in the second
   image.

.. cpp:function::void FindOptimalImageObservations(const Eigen::Matrix3d& E, const Eigen::Vector2d& point1, const Eigen::Vector2d& point2, Eigen::Vector2d* optimal_point1, Eigen::Vector2d* optimal_point2)

.. code-block:: cpp

    void FindOptimalImageObservations(const Eigen::Matrix3d& E,
                                      const Eigen::Vector2d& point1,
                                      const Eigen::Vector2d& point2,
                                      Eigen::Vector2d* optimal_point1,
                                      Eigen::Vector2d* optimal_point2) {
      const Eigen::Vector3d& point1h = point1.homogeneous();
      const Eigen::Vector3d& point2h = point2.homogeneous();

      Eigen::Matrix<double, 2, 3> S;
      S << 1, 0, 0, 0, 1, 0;

      // Epipolar lines.
      Eigen::Vector2d n1 = S * E * point2h;
      Eigen::Vector2d n2 = S * E.transpose() * point1h;

      const Eigen::Matrix2d E_tilde = E.block<2, 2>(0, 0);

      const double a = n1.transpose() * E_tilde * n2;
      const double b = (n1.squaredNorm() + n2.squaredNorm()) / 2.0;
      const double c = point1h.transpose() * E * point2h;
      const double d = sqrt(b * b - a * c);
      double lambda = c / (b + d);

      n1 -= E_tilde * lambda * n1;
      n2 -= E_tilde.transpose() * lambda * n2;

      lambda *= (2.0 * d) / (n1.squaredNorm() + n2.squaredNorm());

      *optimal_point1 = (point1h - S.transpose() * lambda * n1).hnormalized();
      *optimal_point2 = (point2h - S.transpose() * lambda * n2).hnormalized();
    }


EpipoleFromEssentialMatrix
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

计算齐次坐标中极点的位置

-  @param E 3x3 essential matrix.

-  @param left\_image If true, epipole in left image is computed, else
   in right image.

-  @return Epipole in homogeneous coordinates.

.. cpp:function:: Eigen::Vector3d EpipoleFromEssentialMatrix(const Eigen::Matrix3d& E, const bool left_image)

.. code-block:: cpp

    Eigen::Vector3d EpipoleFromEssentialMatrix(const Eigen::Matrix3d& E,
                                               const bool left_image) {
      Eigen::Vector3d e;

      if (left_image) {

        Eigen::JacobiSVD<Eigen::Matrix3d> svd(E, Eigen::ComputeFullV);

        e = svd.matrixV().block<3, 1>(0, 2);

      } else {

        Eigen::JacobiSVD<Eigen::Matrix3d> svd(E.transpose(), Eigen::ComputeFullV);

        e = svd.matrixV().block<3, 1>(0, 2);

      }
      return e;
    }


InvertEssentialMatrix
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

反转基本矩阵，即，如果基本矩阵E描述了从摄像机A到B的转换，则反转的基本矩阵E'描述了从摄像机B到A的转换。

-  @param E 3x3 essential matrix.

-  @return Inverted essential matrix.

.. cpp:function:: Eigen::Matrix3d InvertEssentialMatrix(const Eigen::Matrix3d& E)

.. code-block:: cpp

    Eigen::Matrix3d InvertEssentialMatrix(const Eigen::Matrix3d& E) {
      return E.transpose();
    }


RefineEssentialMatrix
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

使用函数“
RefineRelativePose”将基本矩阵分解为旋转和平移分量，并refine相对位姿。

.. cpp:function:: bool RefineEssentialMatrix(const ceres::Solver::Options& options, const std::vector<Eigen::Vector2d>& points1, const std::vector<Eigen::Vector2d>& points2, const std::vector<char>& inlier_mask, Eigen::Matrix3d* E)

.. code-block:: cpp

    bool RefineEssentialMatrix(const ceres::Solver::Options& options,
                               const std::vector<Eigen::Vector2d>& points1,
                               const std::vector<Eigen::Vector2d>& points2,
                               const std::vector<char>& inlier_mask,
                               Eigen::Matrix3d* E) {
      CHECK_EQ(points1.size(), points2.size());
      CHECK_EQ(points1.size(), inlier_mask.size());

      // 提取内点，将基本矩阵分解为旋转和平移分量。

      size_t num_inliers = 0;
      for (const auto inlier : inlier_mask) {
        if (inlier) {
          num_inliers += 1;
        }
      }

      std::vector<Eigen::Vector2d> inlier_points1(num_inliers);
      std::vector<Eigen::Vector2d> inlier_points2(num_inliers);

      size_t j = 0;

      for (size_t i = 0; i < inlier_mask.size(); ++i) {
        if (inlier_mask[i]) {
          inlier_points1[j] = points1[i];
          inlier_points2[j] = points2[i];
          j += 1;
        }
      }

      // 从基本矩阵中提取相对位姿

      Eigen::Matrix3d R;
      Eigen::Vector3d tvec;
      std::vector<Eigen::Vector3d> points3D;
      PoseFromEssentialMatrix(*E, inlier_points1, inlier_points2, &R, &tvec,
                              &points3D);

      // 旋转矩阵转四元数
      Eigen::Vector4d qvec = RotationMatrixToQuaternion(R);

      if (points3D.size() == 0) {
        return false;
      }

      // refine基本矩阵，refine的过程将本来是外点的点视为内点，从而使用所有点。

      const bool refinement_success =
          RefineRelativePose(options, inlier_points1, inlier_points2, &qvec, &tvec);

      if (!refinement_success) {
        return false;
      }

      // Compose refined essential matrix.
      const Eigen::Matrix3d rot_mat = QuaternionToRotationMatrix(qvec);
      *E = EssentialMatrixFromPose(rot_mat, tvec);

      return true;
    }

Homography Matrix
-----------------

DecomposeHomographyMatrix
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

将单应性矩阵分解为可能的旋转，平移和平面法线向量：

假定第一个位姿为\ :math:`P = [I | 0]`\ 。 注意，如果“
:math:`R.size()== t.size()== n.size()== 4`\ ”，则单应性是plane-induced的。
如果\ :math:`R.size() == t.size() == n.size() == 1`\ ，则单应性是纯旋转的。

Malis, Ezio, and Manuel Vargas. 《Deeper understanding of the homography
decomposition for vision-based control.》 (2007): 90.

-  @param H 3x3 homography matrix.
-  @param K 3x3 calibration matrix.
-  @param R Possible 3x3 rotation matrices.
-  @param t Possible translation vectors.
-  @param n Possible normal vectors.

.. cpp:function:: void DecomposeHomographyMatrix(const Eigen::Matrix3d& H, const Eigen::Matrix3d& K1, const Eigen::Matrix3d& K2, std::vector<Eigen::Matrix3d>* R, std::vector<Eigen::Vector3d>* t, std::vector<Eigen::Vector3d>* n)

.. code-block:: cpp

    void DecomposeHomographyMatrix(const Eigen::Matrix3d& H,
                                   const Eigen::Matrix3d& K1,
                                   const Eigen::Matrix3d& K2,
                                   std::vector<Eigen::Matrix3d>* R,
                                   std::vector<Eigen::Vector3d>* t,
                                   std::vector<Eigen::Vector3d>* n) {
      // Remove calibration from homography.
      Eigen::Matrix3d H_normalized = K2.inverse() * H * K1;

      // Remove scale from normalized homography.
      Eigen::JacobiSVD<Eigen::Matrix3d> hmatrix_norm_svd(H_normalized);
      H_normalized.array() /= hmatrix_norm_svd.singularValues()[1];

      const Eigen::Matrix3d S =
          H_normalized.transpose() * H_normalized - Eigen::Matrix3d::Identity();

      // Check if H is rotation matrix.
      const double kMinInfinityNorm = 1e-3;
      if (S.lpNorm<Eigen::Infinity>() < kMinInfinityNorm) {
        *R = {H_normalized};
        *t = {Eigen::Vector3d::Zero()};
        *n = {Eigen::Vector3d::Zero()};
        return;
      }

      const double M00 = ComputeOppositeOfMinor(S, 0, 0);
      const double M11 = ComputeOppositeOfMinor(S, 1, 1);
      const double M22 = ComputeOppositeOfMinor(S, 2, 2);

      const double rtM00 = std::sqrt(M00);
      const double rtM11 = std::sqrt(M11);
      const double rtM22 = std::sqrt(M22);

      const double M01 = ComputeOppositeOfMinor(S, 0, 1);
      const double M12 = ComputeOppositeOfMinor(S, 1, 2);
      const double M02 = ComputeOppositeOfMinor(S, 0, 2);

      const int e12 = SignOfNumber(M12);
      const int e02 = SignOfNumber(M02);
      const int e01 = SignOfNumber(M01);

      const double nS00 = std::abs(S(0, 0));
      const double nS11 = std::abs(S(1, 1));
      const double nS22 = std::abs(S(2, 2));

      const std::array<double, 3> nS{{nS00, nS11, nS22}};
      const size_t idx =
          std::distance(nS.begin(), std::max_element(nS.begin(), nS.end()));

      Eigen::Vector3d np1;
      Eigen::Vector3d np2;
      if (idx == 0) {
        np1[0] = S(0, 0);
        np2[0] = S(0, 0);
        np1[1] = S(0, 1) + rtM22;
        np2[1] = S(0, 1) - rtM22;
        np1[2] = S(0, 2) + e12 * rtM11;
        np2[2] = S(0, 2) - e12 * rtM11;
      } else if (idx == 1) {
        np1[0] = S(0, 1) + rtM22;
        np2[0] = S(0, 1) - rtM22;
        np1[1] = S(1, 1);
        np2[1] = S(1, 1);
        np1[2] = S(1, 2) - e02 * rtM00;
        np2[2] = S(1, 2) + e02 * rtM00;
      } else if (idx == 2) {
        np1[0] = S(0, 2) + e01 * rtM11;
        np2[0] = S(0, 2) - e01 * rtM11;
        np1[1] = S(1, 2) + rtM00;
        np2[1] = S(1, 2) - rtM00;
        np1[2] = S(2, 2);
        np2[2] = S(2, 2);
      }

      const double traceS = S.trace();
      const double v = 2.0 * std::sqrt(1.0 + traceS - M00 - M11 - M22);

      const double ESii = SignOfNumber(S(idx, idx));
      const double r_2 = 2 + traceS + v;
      const double nt_2 = 2 + traceS - v;

      const double r = std::sqrt(r_2);
      const double n_t = std::sqrt(nt_2);

      const Eigen::Vector3d n1 = np1.normalized();
      const Eigen::Vector3d n2 = np2.normalized();

      const double half_nt = 0.5 * n_t;
      const double esii_t_r = ESii * r;

      const Eigen::Vector3d t1_star = half_nt * (esii_t_r * n2 - n_t * n1);
      const Eigen::Vector3d t2_star = half_nt * (esii_t_r * n1 - n_t * n2);

      const Eigen::Matrix3d R1 =
          ComputeHomographyRotation(H_normalized, t1_star, n1, v);
      const Eigen::Vector3d t1 = R1 * t1_star;

      const Eigen::Matrix3d R2 =
          ComputeHomographyRotation(H_normalized, t2_star, n2, v);
      const Eigen::Vector3d t2 = R2 * t2_star;

      *R = {R1, R1, R2, R2};
      *t = {t1, -t1, t2, -t2};
      *n = {-n1, n1, -n2, n2};
    }

PoseFromHomographyMatrix
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

从给定的单应性矩阵中恢复最可能的位姿。

假定第一个位姿为\ :math:`P = [I | 0]`\ 。

-  @param H 3x3 homography matrix.
-  @param K1 3x3 calibration matrix of first camera.
-  @param K2 3x3 calibration matrix of second camera.
-  @param points1 First set of corresponding points.
-  @param points2 Second set of corresponding points.
-  @param R Most probable 3x3 rotation matrix.
-  @param t Most probable 3x1 translation vector.
-  @param n Most probable 3x1 normal vector.
-  @param points3D Triangulated 3D points infront of camera (only if
   homography is not pure-rotational).

.. cpp:function:: void PoseFromHomographyMatrix(const Eigen::Matrix3d& H, const Eigen::Matrix3d& K1, const Eigen::Matrix3d& K2, const std::vector<Eigen::Vector2d>& points1, const std::vector<Eigen::Vector2d>& points2, Eigen::Matrix3d* R, Eigen::Vector3d* t, Eigen::Vector3d* n, std::vector<Eigen::Vector3d>* points3D)

.. code-block:: cpp

    void PoseFromHomographyMatrix(const Eigen::Matrix3d& H,
                                  const Eigen::Matrix3d& K1,
                                  const Eigen::Matrix3d& K2,
                                  const std::vector<Eigen::Vector2d>& points1,
                                  const std::vector<Eigen::Vector2d>& points2,
                                  Eigen::Matrix3d* R, Eigen::Vector3d* t,
                                  Eigen::Vector3d* n,
                                  std::vector<Eigen::Vector3d>* points3D) {
      CHECK_EQ(points1.size(), points2.size());

      std::vector<Eigen::Matrix3d> R_cmbs;
      std::vector<Eigen::Vector3d> t_cmbs;
      std::vector<Eigen::Vector3d> n_cmbs;
      DecomposeHomographyMatrix(H, K1, K2, &R_cmbs, &t_cmbs, &n_cmbs);

      points3D->clear();
      for (size_t i = 0; i < R_cmbs.size(); ++i) {
        std::vector<Eigen::Vector3d> points3D_cmb;
        CheckCheirality(R_cmbs[i], t_cmbs[i], points1, points2, &points3D_cmb);
        if (points3D_cmb.size() >= points3D->size()) {
          *R = R_cmbs[i];
          *t = t_cmbs[i];
          *n = n_cmbs[i];
          *points3D = points3D_cmb;
        }
      }
    }


HomographyMatrixFromPose
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

根据相对位姿计算单应矩阵

-  @param K1 3x3 calibration matrix of first camera.

-  @param K2 3x3 calibration matrix of second camera.

-  @param R Most probable 3x3 rotation matrix.

-  @param t Most probable 3x1 translation vector.

-  @param n Most probable 3x1 normal vector.

-  @param d Orthogonal distance from plane.

-  @return 3x3 homography matrix.

.. cpp:function:: Eigen::Matrix3d HomographyMatrixFromPose(const Eigen::Matrix3d& K1, const Eigen::Matrix3d& K2, const Eigen::Matrix3d& R, const Eigen::Vector3d& t, const Eigen::Vector3d& n, const double d)

.. code-block:: cpp

    Eigen::Matrix3d HomographyMatrixFromPose(const Eigen::Matrix3d& K1,
                                             const Eigen::Matrix3d& K2,
                                             const Eigen::Matrix3d& R,
                                             const Eigen::Vector3d& t,
                                             const Eigen::Vector3d& n,
                                             const double d) {
      CHECK_GT(d, 0);
      return K2 * (R - t * n.normalized().transpose() / d) * K1.inverse();
    }


Projection Matrix
-----------------

ComposeProjectionMatrix
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

由旋转和平移分量组成投影矩阵。 投影矩阵将3D世界转换为图像点。

-  @param qvec Unit Quaternion rotation coefficients (w, x, y, z).

-  @param tvec 3x1 translation vector.

-  @return 3x4 projection matrix.

.. cpp:function:: Eigen::Matrix3x4d ComposeProjectionMatrix(const Eigen::Vector4d& qvec, const Eigen::Vector3d& tvec)

.. code-block:: cpp

    Eigen::Matrix3x4d ComposeProjectionMatrix(const Eigen::Vector4d& qvec,
                                              const Eigen::Vector3d& tvec) {
      Eigen::Matrix3x4d proj_matrix;
      proj_matrix.leftCols<3>() = QuaternionToRotationMatrix(qvec);
      proj_matrix.rightCols<1>() = tvec;
      return proj_matrix;
    }

-  @param R 3x3 rotation matrix.

-  @param t 3x1 translation vector.

-  @return 3x4 projection matrix.

.. cpp:function:: Eigen::Matrix3x4d ComposeProjectionMatrix(const Eigen::Matrix3d& R, const Eigen::Vector3d& T)

.. code-block:: cpp

    Eigen::Matrix3x4d ComposeProjectionMatrix(const Eigen::Matrix3d& R,
                                              const Eigen::Vector3d& T) {
      Eigen::Matrix3x4d proj_matrix;
      proj_matrix.leftCols<3>() = R;
      proj_matrix.rightCols<1>() = T;
      return proj_matrix;
    }


InvertProjectionMatrix
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

反转投影矩阵，定义为：

.. math::  P = [R | t]~~ ~~with~~ ~~R \in SO(3) ~~~and~~~ t \in R^3

-  param proj\_matrix 3x4 projection matrix.

-  @return 3x4 inverse projection matrix.

.. cpp:function:: Eigen::Matrix3x4d InvertProjectionMatrix(const Eigen::Matrix3x4d& proj_matrix)

.. code-block::

    Eigen::Matrix3x4d InvertProjectionMatrix(const Eigen::Matrix3x4d& proj_matrix) {
      Eigen::Matrix3x4d inv_proj_matrix;
      inv_proj_matrix.leftCols<3>() = proj_matrix.leftCols<3>().transpose();
      inv_proj_matrix.rightCols<1>() = ProjectionCenterFromMatrix(proj_matrix);
      return inv_proj_matrix;
    }

.. cpp:function:: Eigen::Vector3d ProjectionCenterFromMatrix(const Eigen::Matrix3x4d& proj_matrix)

.. code-block:: cpp

    Eigen::Vector3d ProjectionCenterFromMatrix(
        const Eigen::Matrix3x4d& proj_matrix) {
      return -proj_matrix.leftCols<3>().transpose() * proj_matrix.rightCols<1>();
    }


ComputeClosestRotationMatrix
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

通过将给定矩阵的奇异值设置为1.计算最接近Frobenius范数的闭合旋转矩阵。

.. cpp:function:: Eigen::Matrix3d ComputeClosestRotationMatrix(const Eigen::Matrix3d& matrix)

.. code-block:: cpp

    Eigen::Matrix3d ComputeClosestRotationMatrix(const Eigen::Matrix3d& matrix) {
      const Eigen::JacobiSVD<Eigen::Matrix3d> svd(
          matrix, Eigen::ComputeFullU | Eigen::ComputeFullV);
      Eigen::Matrix3d R = svd.matrixU() * (svd.matrixV().transpose());
      if (R.determinant() < 0.0) {
        R *= -1.0;
      }
      return R;
    }


DecomposeProjectionMatrix
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

将投影矩阵分解为内参，旋转矩阵和平移向量。

.. cpp:function:: bool DecomposeProjectionMatrix(const Eigen::Matrix3x4d& P, Eigen::Matrix3d* K, Eigen::Matrix3d* R, Eigen::Vector3d* T)

.. code-block:: cpp

    bool DecomposeProjectionMatrix(const Eigen::Matrix3x4d& P, Eigen::Matrix3d* K,
                                   Eigen::Matrix3d* R, Eigen::Vector3d* T) {
      Eigen::Matrix3d RR;
      Eigen::Matrix3d QQ;
      DecomposeMatrixRQ(P.leftCols<3>().eval(), &RR, &QQ);

      *R = ComputeClosestRotationMatrix(QQ);

      const double det_K = RR.determinant();
      if (det_K == 0) {
        return false;
      } else if (det_K > 0) {
        *K = RR;
      } else {
        *K = -RR;
      }

      for (int i = 0; i < 3; ++i) {
        if ((*K)(i, i) < 0.0) {
          K->col(i) = -K->col(i);
          R->row(i) = -R->row(i);
        }
      }

      *T = K->triangularView<Eigen::Upper>().solve(P.col(3));
      if (det_K < 0) {
        *T = -(*T);
      }

      return true;
    }


ProjectPointToImage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

将3D投影到图像

-  @param points3D 3D world point as 3x1 vector.

-  @param proj\_matrix 3x4 projection matrix.

-  @param camera Camera used to project to image plane.

-  @return Projected image point.

.. cpp:function:: Eigen::Vector2d ProjectPointToImage(const Eigen::Vector3d& point3D, const Eigen::Matrix3x4d& proj_matrix, const Camera& camera)

.. code-block:: cpp

    Eigen::Vector2d ProjectPointToImage(const Eigen::Vector3d& point3D,
                                        const Eigen::Matrix3x4d& proj_matrix,
                                        const Camera& camera) {
      const Eigen::Vector3d world_point = proj_matrix * point3D.homogeneous();
      return camera.WorldToImage(world_point.hnormalized());
    }


CalculateSquaredReprojectionError
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

计算重投影误差

重投影误差是图像中的观测值与3D点在图像中的投影之间的欧式距离。
如果3D点在相机后面，则此函数返回DBL\_MAX。

.. cpp:function:: double CalculateSquaredReprojectionError(const Eigen::Vector2d& point2D, const Eigen::Vector3d& point3D, const Eigen::Vector4d& qvec, const Eigen::Vector3d& tvec, const Camera& camera)

.. code-block:: cpp

    double CalculateSquaredReprojectionError(const Eigen::Vector2d& point2D,
                                             const Eigen::Vector3d& point3D,
                                             const Eigen::Vector4d& qvec,
                                             const Eigen::Vector3d& tvec,
                                             const Camera& camera) {
      const Eigen::Vector3d proj_point3D =
          QuaternionRotatePoint(qvec, point3D) + tvec;

      // Check that point is infront of camera.
      if (proj_point3D.z() < std::numeric_limits<double>::epsilon()) {
        return std::numeric_limits<double>::max();
      }

      const Eigen::Vector2d proj_point2D =
          camera.WorldToImage(proj_point3D.hnormalized());

      return (proj_point2D - point2D).squaredNorm();
    }

.. cpp:function:: double CalculateSquaredReprojectionError(const Eigen::Vector2d& point2D, const Eigen::Vector3d& point3D, const Eigen::Matrix3x4d& proj_matrix, const Camera& camera)

.. code-block:: cpp

    double CalculateSquaredReprojectionError(const Eigen::Vector2d& point2D,
                                             const Eigen::Vector3d& point3D,
                                             const Eigen::Matrix3x4d& proj_matrix,
                                             const Camera& camera) {
      const double proj_z = proj_matrix.row(2).dot(point3D.homogeneous());

      // Check that point is infront of camera.
      if (proj_z < std::numeric_limits<double>::epsilon()) {
        return std::numeric_limits<double>::max();
      }

      const double proj_x = proj_matrix.row(0).dot(point3D.homogeneous());
      const double proj_y = proj_matrix.row(1).dot(point3D.homogeneous());
      const double inv_proj_z = 1.0 / proj_z;

      const Eigen::Vector2d proj_point2D = camera.WorldToImage(
          Eigen::Vector2d(inv_proj_z * proj_x, inv_proj_z * proj_y));

      return (proj_point2D - point2D).squaredNorm();
    }


CalculateAngularError
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

计算角度误差

角度误差是从相机中心到3D点的观察到的光线与实际的光线之间的角度。

.. cpp:function:: double CalculateAngularError(const Eigen::Vector2d& point2D, const Eigen::Vector3d& point3D, const Eigen::Vector4d& qvec, const Eigen::Vector3d& tvec, const Camera& camera)

.. code-block:: cpp

    double CalculateAngularError(const Eigen::Vector2d& point2D,
                                 const Eigen::Vector3d& point3D,
                                 const Eigen::Vector4d& qvec,
                                 const Eigen::Vector3d& tvec,
                                 const Camera& camera) {
      return CalculateNormalizedAngularError(camera.ImageToWorld(point2D), point3D,
                                             qvec, tvec);
    }

.. cpp:function:: double CalculateAngularError(const Eigen::Vector2d& point2D, const Eigen::Vector3d& point3D, const Eigen::Matrix3x4d& proj_matrix, const Camera& camera)

.. code-block:: cpp

    double CalculateAngularError(const Eigen::Vector2d& point2D,
                                 const Eigen::Vector3d& point3D,
                                 const Eigen::Matrix3x4d& proj_matrix,
                                 const Camera& camera) {
      return CalculateNormalizedAngularError(camera.ImageToWorld(point2D), point3D,
                                             proj_matrix);
    }


CalculateNormalizedAngularError
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

使用归一化的图像点计算角度误差

角度误差是从相机中心到3D点的观察到的光线与实际的光线之间的角度。

.. cpp:function:: double CalculateNormalizedAngularError(const Eigen::Vector2d& point2D, const Eigen::Vector3d& point3D, const Eigen::Vector4d& qvec, const Eigen::Vector3d& tvec)

.. code-block:: cpp

    double CalculateNormalizedAngularError(const Eigen::Vector2d& point2D,
                                           const Eigen::Vector3d& point3D,
                                           const Eigen::Vector4d& qvec,
                                           const Eigen::Vector3d& tvec) {
      const Eigen::Vector3d ray1 = point2D.homogeneous();
      const Eigen::Vector3d ray2 = QuaternionRotatePoint(qvec, point3D) + tvec;
      return std::acos(ray1.normalized().transpose() * ray2.normalized());
    }

.. cpp:function:: double CalculateNormalizedAngularError(const Eigen::Vector2d& point2D, const Eigen::Vector3d& point3D, const Eigen::Matrix3x4d& proj_matrix)

.. code-block:: cpp

    double CalculateNormalizedAngularError(const Eigen::Vector2d& point2D,
                                           const Eigen::Vector3d& point3D,
                                           const Eigen::Matrix3x4d& proj_matrix) {
      const Eigen::Vector3d ray1 = point2D.homogeneous();
      const Eigen::Vector3d ray2 = proj_matrix * point3D.homogeneous();
      return std::acos(ray1.normalized().transpose() * ray2.normalized());
    }


CalculateDepth
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

计算相对于相机的3D点深度

深度定义为3D点到相机的欧式距离，如果3D点在相机的前面，则为正，如果在相机的后面，则为负。

-  @param proj\_matrix 3x4 projection matrix.

-  @param point3D 3D point as 3x1 vector.

-  @return Depth of 3D point.

.. cpp:function:: double CalculateDepth(const Eigen::Matrix3x4d& proj_matrix, const Eigen::Vector3d& point3D)

.. code-block:: cpp

    double CalculateDepth(const Eigen::Matrix3x4d& proj_matrix,
                          const Eigen::Vector3d& point3D) {
      const double proj_z = proj_matrix.row(2).dot(point3D.homogeneous());
      return proj_z * proj_matrix.col(2).norm();
    }

HasPointPositiveDepth
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

检查3D点是否通过了cheirality约束

也就是说，它位于相机前面而不是图像平面中。

.. cpp:function:: bool HasPointPositiveDepth(const Eigen::Matrix3x4d& proj_matrix, const Eigen::Vector3d& point3D)

.. code-block:: cpp

    bool HasPointPositiveDepth(const Eigen::Matrix3x4d& proj_matrix,
                               const Eigen::Vector3d& point3D) {
      return proj_matrix.row(2).dot(point3D.homogeneous()) >=
             std::numeric_limits<double>::epsilon();
    }

