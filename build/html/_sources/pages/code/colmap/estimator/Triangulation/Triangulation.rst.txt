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

SetMinTriAngle
~~~~~~~~~~~~~~~

   设置最小三角剖分角度

   .. cpp:function:: void TriangulationEstimator::SetMinTriAngle(const double min_tri_angle);

   .. code-block:: cpp

      void TriangulationEstimator::SetMinTriAngle(const double min_tri_angle) {
        CHECK_GE(min_tri_angle, 0);
        min_tri_angle_ = min_tri_angle;
      }

SetResidualType
~~~~~~~~~~~~~~~~~~~~~~

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

Estimate
~~~~~~~~~~~~~~~

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

            const M_t xyz = TriangulatePoint(
               pose_data[0].proj_matrix, pose_data[1].proj_matrix,
               point_data[0].point_normalized, point_data[1].point_normalized);

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

             // 检查cheirality约束
             for (const auto& pose : pose_data) {
               if (!HasPointPositiveDepth(pose.proj_matrix, xyz))
               return std::vector<M_t>();
             }

            // 检查三角剖分角度
            for (size_t i = 0; i < pose_data.size(); ++i) {
               for (size_t j = 0; j < i; ++j) {
               const double tri_angle = CalculateTriangulationAngle(
                  pose_data[i].proj_center, pose_data[j].proj_center, xyz);
               if (tri_angle >= min_tri_angle_)
                  return std::vector<M_t>{xyz};
               }
            }
         }

         return std::vector<M_t>();
      }

Residuals
~~~~~~~~~~~~~~~

   .. cpp:function:: void TriangulationEstimator::Residuals(const std::vector<X_t>& point_data,const std::vector<Y_t>& pose_data,const M_t& xyz,std::vector<double>* residuals)

   .. code-block:: cpp

      void TriangulationEstimator::Residuals(const std::vector<X_t>& point_data,
                                             const std::vector<Y_t>& pose_data,
                                             const M_t& xyz,
                                             std::vector<double>* residuals) const {
         CHECK_EQ(point_data.size(), pose_data.size());

         residuals->resize(point_data.size());


         for (size_t i = 0; i < point_data.size(); ++i) {
            // 如果残差类型是重投影误差
            if (residual_type_ == ResidualType::REPROJECTION_ERROR) {
               (*residuals)[i] = CalculateSquaredReprojectionError(
                  point_data[i].point, xyz, pose_data[i].proj_matrix,
                  *pose_data[i].camera);
            }

            // 如果残差类型是重投影误差
            else if (residual_type_ == ResidualType::ANGULAR_ERROR) {
               const double angular_error = CalculateNormalizedAngularError(
                  point_data[i].point_normalized, xyz, pose_data[i].proj_matrix);
               (*residuals)[i] = angular_error * angular_error;
            }
         }
      }


EstimateTriangulation
~~~~~~~~~~~~~~~~~~~~~~~~

   .. cpp:function:: bool EstimateTriangulation(const EstimateTriangulationOptions& options,const std::vector<TriangulationEstimator::PointData>& point_data,const std::vector<TriangulationEstimator::PoseData>& pose_data,std::vector<char>* inlier_mask, Eigen::Vector3d* xyz)

   .. code-block:: cpp


      bool EstimateTriangulation(
            const EstimateTriangulationOptions& options,
            const std::vector<TriangulationEstimator::PointData>& point_data,
            const std::vector<TriangulationEstimator::PoseData>& pose_data,
            std::vector<char>* inlier_mask, Eigen::Vector3d* xyz) {
         CHECK_NOTNULL(inlier_mask);
         CHECK_NOTNULL(xyz);
         CHECK_GE(point_data.size(), 2);
         CHECK_EQ(point_data.size(), pose_data.size());
         options.Check();

         // 使用LORANSAC方法鲁棒的估算轨道
         LORANSAC<TriangulationEstimator, TriangulationEstimator,
                 InlierSupportMeasurer, CombinationSampler> ransac(options.ransac_options);

         // 设置最小三角剖分角度
         ransac.estimator.SetMinTriAngle(options.min_tri_angle);

         // 设置残差类型
         ransac.estimator.SetResidualType(options.residual_type);

         // 设置局部估计最小三角剖分角度
         ransac.local_estimator.SetMinTriAngle(options.min_tri_angle);

         // 设置局部估计残差类型
         ransac.local_estimator.SetResidualType(options.residual_type);

         // LORANSAC方法计算三角剖分
         const auto report = ransac.Estimate(point_data, pose_data);
         if (!report.success) {
            return false;
         }

         // 得到inlier掩码和三维坐标xyz
         *inlier_mask = report.inlier_mask;
         *xyz = report.model;

         return report.success;
      }
