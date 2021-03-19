Triangulation
==========================

三角剖分估计器可从多个观测值中估计3D点。

.. important::
   三角剖分必须满足以下约束：
   1. 观测对之间的足够的三角剖分角度。
   2. 所有观察值都必须满足cheirality约束

观察结果由图像测量值以及相应的相机位姿和标定组成。

.. cpp:class:: TriangulationEstimator

结构体
----------------

.. cpp:struct:: PointData

.. code-block:: cpp

   struct PointData {
      EIGEN_MAKE_ALIGNED_OPERATOR_NEW
      PointData() {}
      PointData(const Eigen::Vector2d& point_, const Eigen::Vector2d& point_N_)
        : point(point_), point_normalized(point_N_) {}

      // 以像素为单位的图像观察值
      Eigen::Vector2d point;

      // 归一化图像观察值
      Eigen::Vector2d point_normalized;
   };

.. cpp:struct:: PoseData

.. code-block:: cpp

   struct PoseData {
      EIGEN_MAKE_ALIGNED_OPERATOR_NEW
      PoseData() : camera(nullptr) {}
      PoseData(const Eigen::Matrix3x4d& proj_matrix_,
             const Eigen::Vector3d& pose_, const Camera* camera_)
        : proj_matrix(proj_matrix_), proj_center(pose_), camera(camera_) {}

      // 观测图像的投影矩阵
      Eigen::Matrix3x4d proj_matrix;

      // 观测图像的投影中心
      Eigen::Vector3d proj_center;

      // 用于观察图像的相机
      const Camera* camera;
   };



成员变量
-----------------

.. cpp:type:: PointData TriangulationEstimator::X_t;

.. cpp:type:: PoseData TriangulationEstimator::Y_t;

.. important::

   这里特别要注意，X_t是点的数据，而Y_t是位姿数据

.. cpp:type:: Eigen::Vector3d TriangulationEstimator::M_t;

.. cpp:member:: static const int TriangulationEstimator::kMinNumSamples = 2;

成员函数
-----------------

1. **SetMinTriAngle**

   设置最小三角剖分角度

.. cpp:function:: void TriangulationEstimator::SetMinTriAngle(const double min_tri_angle);

.. code-block:: cpp

   void TriangulationEstimator::SetMinTriAngle(const double min_tri_angle) {
     CHECK_GE(min_tri_angle, 0);
     min_tri_angle_ = min_tri_angle;
   }

2. **SetResidualType**

   设置残差类型

   .. code-block::

      enum class ResidualType {
         ANGULAR_ERROR,
         REPROJECTION_ERROR,
      };

.. cpp:function:: void TriangulationEstimator::SetResidualType(const ResidualType residual_type);

.. code-block:: cpp

   void TriangulationEstimator::SetResidualType(const ResidualType residual_type) {
     residual_type_ = residual_type;
   }

3. **Estimate**

   从两视图观察值估计3D点

   .. cpp:function:: std::vector<TriangulationEstimator::M_t> TriangulationEstimator::Estimate(const std::vector<X_t>& point_data,const std::vector<Y_t>& pose_data)

   .. code-block:: cpp

      std::vector<TriangulationEstimator::M_t> TriangulationEstimator::Estimate(
         const std::vector<X_t>& point_data,
         const std::vector<Y_t>& pose_data) const {

            CHECK_GE(point_data.size(), 2);
            CHECK_EQ(point_data.size(), pose_data.size());

            if (point_data.size() == 2) {

            // 两视图三角剖分

            // 得到三维点xyz
            const M_t xyz = TriangulatePoint(
               pose_data[0].proj_matrix, pose_data[1].proj_matrix,
               point_data[0].point_normalized, point_data[1].point_normalized);

            // 检测3D点是否通过了cheirality约束 并且 计算三角剖分角度是否大于最小值
            if (HasPointPositiveDepth(pose_data[0].proj_matrix, xyz) &&
               HasPointPositiveDepth(pose_data[1].proj_matrix, xyz) &&
               CalculateTriangulationAngle(pose_data[0].proj_center,
                                          pose_data[1].proj_center,
                                          xyz) >= min_tri_angle_) {
               return std::vector<M_t>{xyz};
            }
         } else {
            // 多视图三角剖分

            std::vector<Eigen::Matrix3x4d> proj_matrices;
            proj_matrices.reserve(point_data.size());
            std::vector<Eigen::Vector2d> points;
            points.reserve(point_data.size());
            for (size_t i = 0; i < point_data.size(); ++i) {
               proj_matrices.push_back(pose_data[i].proj_matrix);
               points.push_back(point_data[i].point_normalized);
            }

            const M_t xyz = TriangulateMultiViewPoint(proj_matrices, points);

            // Check for cheirality constraint.
            for (const auto& pose : pose_data) {
               if (!HasPointPositiveDepth(pose.proj_matrix, xyz)) {
               return std::vector<M_t>();
               }
            }

            // Check for sufficient triangulation angle.
            for (size_t i = 0; i < pose_data.size(); ++i) {
               for (size_t j = 0; j < i; ++j) {
                  const double tri_angle = CalculateTriangulationAngle(
                     pose_data[i].proj_center, pose_data[j].proj_center, xyz);
               if (tri_angle >= min_tri_angle_) {
                  return std::vector<M_t>{xyz};
               }
            }
          }
        }

         return std::vector<M_t>();
      }

