Pose
===========

结构体
-----------

.. cpp:struct:: AbsolutePoseEstimationOptions

.. code-block:: cpp

   struct AbsolutePoseEstimationOptions {
     // 是否估计焦距
     bool estimate_focal_length = false;

     // 用于焦距估计的离散样本数
     size_t num_focal_length_samples = 30;

     // 在给定相机焦距附近进行离散焦距采样的最小焦距比
     double min_focal_length_ratio = 0.2;

     // 在给定相机焦距附近进行离散焦距采样的最大焦距比
     double max_focal_length_ratio = 5;

     // 并行估计焦距的线程数
     int num_threads = ThreadPool::kMaxNumThreads;

     // 用于P3P RANSAC的选项
     RANSACOptions ransac_options;

     void Check() const {
       CHECK_GT(num_focal_length_samples, 0);
       CHECK_GT(min_focal_length_ratio, 0);
       CHECK_GT(max_focal_length_ratio, 0);
       CHECK_LT(min_focal_length_ratio, max_focal_length_ratio);
       ransac_options.Check();
     }
   };


.. cpp:struct:: AbsolutePoseRefinementOptions

.. code-block:: cpp

   struct AbsolutePoseRefinementOptions {
     // 收敛准则
     double gradient_tolerance = 1.0;

     // 求解器最大迭代次数
     int max_num_iterations = 100;

     // Scaling factor determines at which residual robustification takes place.
     // 尺度因子决定了发生残留鲁棒性的位置
     double loss_function_scale = 1.0;

     // 是否优化焦距参数组
     bool refine_focal_length = true;

     // 是否优化额外参数组
     bool refine_extra_params = true;

     // 是否打印summary
     bool print_summary = true;

     void Check() const {
       CHECK_GE(gradient_tolerance, 0.0);
       CHECK_GE(max_num_iterations, 0);
       CHECK_GE(loss_function_scale, 0.0);
     }
   };

成员变量
---------

.. cpp:type:: LORANSAC<P3PEstimator, EPNPEstimator> AbsolutePoseRANSAC;


成员函数
-----------------

EstimateAbsolutePoseKernel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   .. cpp:function:: void EstimateAbsolutePoseKernel(const Camera& camera,const double focal_length_factor,const std::vector<Eigen::Vector2d>& points2D,const std::vector<Eigen::Vector3d>& points3D,const RANSACOptions& options,AbsolutePoseRANSAC::Report* report)

   .. code-block:: cpp

      void EstimateAbsolutePoseKernel(const Camera& camera,
                                   const double focal_length_factor,
                                   const std::vector<Eigen::Vector2d>& points2D,
                                   const std::vector<Eigen::Vector3d>& points3D,
                                   const RANSACOptions& options,
                                   AbsolutePoseRANSAC::Report* report) {

         Camera scaled_camera = camera;

         const std::vector<size_t>& focal_length_idxs = camera.FocalLengthIdxs();

         // 按尺度因子缩放焦距
         for (const size_t idx : focal_length_idxs) {
          scaled_camera.Params(idx) *= focal_length_factor;
         }

         // 使用缩放焦距后的相机(with current camera hypothesis)对图像坐标进行归一化
         std::vector<Eigen::Vector2d> points2D_N(points2D.size());

         for (size_t i = 0; i < points2D.size(); ++i) {
          points2D_N[i] = scaled_camera.ImageToWorld(points2D[i]);
         }

         // 估计给定焦距的位姿
         auto custom_options = options;

         custom_options.max_error =
            scaled_camera.ImageToWorldThreshold(options.max_error);

         // 定义一个P3P和EPnP的求解器
         AbsolutePoseRANSAC ransac(custom_options);

         // 求解返回位姿变换矩阵
         *report = ransac.Estimate(points2D_N, points3D);
      }

EstimateAbsolutePose
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   根据2D-3D对应关系估算绝对姿势（焦距可选）

   使用给定相机的焦距周围的离散采样执行焦距估计。 导致最大的inliers的焦距被分配给给定的摄像机。

   .. cpp:function:: bool EstimateAbsolutePose(const AbsolutePoseEstimationOptions& options,const std::vector<Eigen::Vector2d>& points2D,const std::vector<Eigen::Vector3d>& points3D,Eigen::Vector4d* qvec, Eigen::Vector3d* tvec,Camera* camera, size_t* num_inliers,std::vector<char>* inlier_mask);

   .. code-block:: cpp

      bool EstimateAbsolutePose(const AbsolutePoseEstimationOptions& options,
                                const std::vector<Eigen::Vector2d>& points2D,
                                const std::vector<Eigen::Vector3d>& points3D,
                                Eigen::Vector4d* qvec, Eigen::Vector3d* tvec,
                                Camera* camera, size_t* num_inliers,
                                std::vector<char>* inlier_mask) {
        options.Check();

        std::vector<double> focal_length_factors;

         if (options.estimate_focal_length) {
          // 使用二次函数生成焦距因子，以便为较小的焦距绘制更多样本
          focal_length_factors.reserve(options.num_focal_length_samples + 1);
          const double fstep = 1.0 / options.num_focal_length_samples;
          const double fscale =
              options.max_focal_length_ratio - options.min_focal_length_ratio;
          for (double f = 0; f <= 1.0; f += fstep) {
            focal_length_factors.push_back(options.min_focal_length_ratio +
                                           fscale * f * f);
            }
         } else {
            focal_length_factors.reserve(1);
            focal_length_factors.push_back(1);
         }

         // future对象提供访问异步操作结果的机制，很轻松解决从异步任务中返回结果。
         std::vector<std::future<void>> futures;
         futures.resize(focal_length_factors.size());
         std::vector<typename AbsolutePoseRANSAC::Report,
                    Eigen::aligned_allocator<typename AbsolutePoseRANSAC::Report>>
            reports;
         reports.resize(focal_length_factors.size( ));

         ThreadPool thread_pool(std::min(
            options.num_threads, static_cast<int>(focal_length_factors.size())));

         // 使用多线程估计相机变换矩阵
         for (size_t i = 0; i < focal_length_factors.size(); ++i) {
            futures[i] = thread_pool.AddTask(
               EstimateAbsolutePoseKernel, *camera, focal_length_factors[i], points2D,
               points3D, options.ransac_options, &reports[i]);
         }

         double focal_length_factor = 0;
         Eigen::Matrix3x4d proj_matrix;
         *num_inliers = 0;
         inlier_mask->clear();

         // 找到最佳model
         for (size_t i = 0; i < focal_length_factors.size(); ++i) {
            // 当共享状态就绪时，返回存储在共享状态中的值(或抛出异常)
            futures[i].get();
            const auto report = reports[i];
            if (report.success && report.support.num_inliers > *num_inliers) {
               *num_inliers = report.support.num_inliers;
               proj_matrix = report.model;
               *inlier_mask = report.inlier_mask;
               focal_length_factor = focal_length_factors[i];
            }
         }

         if (*num_inliers == 0) {
            return false;
         }

         // 以最佳估计焦距缩放输出相机
         if (options.estimate_focal_length && *num_inliers > 0) {
            const std::vector<size_t>& focal_length_idxs = camera->FocalLengthIdxs();
            for (const size_t idx : focal_length_idxs) {
               camera->Params(idx) *= focal_length_factor;
            }
         }

         // 提取位姿参数
         *qvec = RotationMatrixToQuaternion(proj_matrix.leftCols<3>());
         *tvec = proj_matrix.rightCols<1>();

         if (IsNaN(*qvec) || IsNaN(*tvec)) {
            return false;
         }

         return true;
      }

   .. note::

      整个函数的步骤为：

      1. 如果选择了使用估计焦距（即没有给定焦距）， 则通过二次函数来生成焦距因子。

      根据样本数的不同，取相同的采样频率:

      .. code-block:: cpp

         const double fstep = 1.0 / options.num_focal_length_samples;

      用最大可能的焦距系数 - 最小可能的焦距系数来作为尺度放缩因子：

      .. code-block:: cpp

         const double fscale = options.max_focal_length_ratio - options.min_focal_length_ratio;

      如果给定焦距，则直接填入即可。

      2. 通过多线程的异步操作计算位姿变换矩阵，future对象提供访问异步操作结果的机制，从异步任务中返回结果。

      对于每一个焦距因子（如果使用估计焦距的话），都会调用一个线程执行 :cpp:func:`EstimateAbsolutePoseKernel` 函数来估计该焦距下的相机位姿变换矩阵。使用P3P或EPnP的方法进行计算，将结果存入到futures中。

      .. code-block:: cpp

        for (size_t i = 0; i < focal_length_factors.size(); ++i) {
          futures[i] = thread_pool.AddTask(
              EstimateAbsolutePoseKernel, *camera, focal_length_factors[i], points2D,
              points3D, options.ransac_options, &reports[i]);
        }

      3. 遍历所有的焦距（如果使用估计焦距的话），找到inliers最大的一组作为最佳model。

      .. code-block:: cpp

         for (size_t i = 0; i < focal_length_factors.size(); ++i) {
            // 当共享状态就绪时，返回存储在共享状态中的值(或抛出异常)
            futures[i].get();
            const auto report = reports[i];
            if (report.success && report.support.num_inliers > *num_inliers) {
               *num_inliers = report.support.num_inliers;
               proj_matrix = report.model;
               *inlier_mask = report.inlier_mask;
               focal_length_factor = focal_length_factors[i];
            }
         }

      \*4. 将相机的焦距乘以最佳model对应的焦距因子

      .. code-block:: cpp

         camera->Params(idx) *= focal_length_factor;

      5. 从位姿变换矩阵中提取位姿（R，t）

      .. code-block:: cpp

         *qvec = RotationMatrixToQuaternion(proj_matrix.leftCols<3>());
         *tvec = proj_matrix.rightCols<1>();

EstimateRelativePose
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   从2D-2D对应关系估计相对值

   假定第一台摄像机的位姿是在原点且没有旋转。第二个相机的位姿作为世界到图像的转换而给出，即：

   .. math::

      x_2 = [R | t] * X_2

   .. cpp:function:: size_t EstimateRelativePose(const RANSACOptions& ransac_options,const std::vector<Eigen::Vector2d>& points1,const std::vector<Eigen::Vector2d>& points2,Eigen::Vector4d* qvec, Eigen::Vector3d* tvec);

   .. code-block:: cpp

      size_t EstimateRelativePose(const RANSACOptions& ransac_options,
                            const std::vector<Eigen::Vector2d>& points1,
                            const std::vector<Eigen::Vector2d>& points2,
                            Eigen::Vector4d* qvec, Eigen::Vector3d* tvec) {

         // 定义五点法本质矩阵求解器
         RANSAC<EssentialMatrixFivePointEstimator> ransac(ransac_options);

         // 求解两个点集之间的本质矩阵E
         const auto report = ransac.Estimate(points1, points2);

         if (!report.success) {
          return 0;
         }

         std::vector<Eigen::Vector2d> inliers1(report.support.num_inliers);
         std::vector<Eigen::Vector2d> inliers2(report.support.num_inliers);

         // 内点遮罩
         size_t j = 0;
         for (size_t i = 0; i < points1.size(); ++i) {
            if (report.inlier_mask[i]) {
               inliers1[j] = points1[i];
               inliers2[j] = points2[i];
               j += 1;
            }
         }

         Eigen::Matrix3d R;

         // 通过本质矩阵恢复R、t
         std::vector<Eigen::Vector3d> points3D;
         PoseFromEssentialMatrix(report.model, inliers1, inliers2, &R, tvec,
                                &points3D);

         // 由旋转矩阵获得旋转四元数
         *qvec = RotationMatrixToQuaternion(R);

         if (IsNaN(*qvec) || IsNaN(*tvec)) {
            return 0;
         }

         // 返回3D点的个数
         return points3D.size();
      }

   .. note::

      整个函数的步骤为：

      1. 定义本质矩阵的RANSAC求解器，通过pt1和pt2计算本质矩阵

      .. code-block:: cpp

         RANSAC<EssentialMatrixFivePointEstimator> ransac(ransac_options);

         const auto report = ransac.Estimate(points1, points2);

      2. 内点遮罩，将需要计算的点存入到inliers1和inliers2中

      .. code-block:: cpp

         if (report.inlier_mask[i]) {
            inliers1[j] = points1[i];
            inliers2[j] = points2[i];
            j += 1;
          }

      3. 分解本质矩阵得到位姿

      .. code-block:: cpp

         PoseFromEssentialMatrix(report.model, inliers1, inliers2, &R, tvec, &points3D);


RefineAbsolutePose
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   从2D-3D对应关系中细化绝对位姿（焦距可选）

   .. cpp:function:: bool RefineAbsolutePose(const AbsolutePoseRefinementOptions& options,const std::vector<char>& inlier_mask,const std::vector<Eigen::Vector2d>& points2D,const std::vector<Eigen::Vector3d>& points3D,Eigen::Vector4d* qvec, Eigen::Vector3d* tvec,Camera* camera);

   .. code-block:: cpp

      bool RefineAbsolutePose(const AbsolutePoseRefinementOptions& options,
                              const std::vector<char>& inlier_mask,
                              const std::vector<Eigen::Vector2d>& points2D,
                              const std::vector<Eigen::Vector3d>& points3D,
                              Eigen::Vector4d* qvec, Eigen::Vector3d* tvec,
                              Camera* camera) {
         CHECK_EQ(inlier_mask.size(), points2D.size());
         CHECK_EQ(points2D.size(), points3D.size());
         options.Check();

         // 定义损失函数 LossFunction 为 柯西核函数
         ceres::LossFunction* loss_function =
            new ceres::CauchyLoss(options.loss_function_scale);

         double* camera_params_data = camera->ParamsData();
         double* qvec_data = qvec->data();
         double* tvec_data = tvec->data();

         std::vector<Eigen::Vector3d> points3D_copy = points3D;

         // 构建最小二乘问题
         ceres::Problem problem;

         for (size_t i = 0; i < points2D.size(); ++i) {
            // 跳过 outlier 观测值
            if (!inlier_mask[i]) {
               continue;
            }

         // 定义代价函数 负责计算残差和雅可比矩阵的向量
         ceres::CostFunction* cost_function = nullptr;

         // \表示下一行属于上一行的末尾（续行）

         // 对相机模型的2D点进行BA代价函数的定义
         switch (camera->ModelId()) {
      #define CAMERA_MODEL_CASE(CameraModel)                                  \
         case CameraModel::kModelId:                                           \
            cost_function =                                                     \
               BundleAdjustmentCostFunction<CameraModel>::Create(points2D[i]); \
            break;

            CAMERA_MODEL_SWITCH_CASES

      #undef CAMERA_MODEL_CASE
            }

            // 为最小二乘求解设置参数
            problem.AddResidualBlock(cost_function, loss_function, qvec_data, tvec_data,
                                   points3D_copy[i].data(), camera_params_data);

            // 设定对应的参数模块在优化过程中保持不变
            problem.SetParameterBlockConstant(points3D_copy[i].data());
         }

         // 残差向量的大小 > 0 （通过对所有残差块的大小求和而获得的）
         if (problem.NumResiduals() > 0) {
            // 四元数参数化
            *qvec = NormalizeQuaternion(*qvec);
            ceres::LocalParameterization* quaternion_parameterization =
               new ceres::QuaternionParameterization;
            problem.SetParameterization(qvec_data, quaternion_parameterization);

            // 相机参数化
            if (!options.refine_focal_length && !options.refine_extra_params) {
               problem.SetParameterBlockConstant(camera->ParamsData());
            } else {
               // 始终固定主点
               std::vector<int> camera_params_const;
               const std::vector<size_t>& principal_point_idxs =
                  camera->PrincipalPointIdxs();
               camera_params_const.insert(camera_params_const.end(),
                                       principal_point_idxs.begin(),
                                       principal_point_idxs.end());

               if (!options.refine_focal_length) {
                  const std::vector<size_t>& focal_length_idxs = camera->FocalLengthIdxs();
                  camera_params_const.insert(camera_params_const.end(),
                                         focal_length_idxs.begin(),
                                         focal_length_idxs.end());
               }

               if (!options.refine_extra_params) {
                  const std::vector<size_t>& extra_params_idxs = camera->ExtraParamsIdxs();
                  camera_params_const.insert(camera_params_const.end(),
                                         extra_params_idxs.begin(),
                                         extra_params_idxs.end());
               }

               if (camera_params_const.size() == camera->NumParams()) {
                  problem.SetParameterBlockConstant(camera->ParamsData());
               } else {
                  ceres::SubsetParameterization* camera_params_parameterization =
                     new ceres::SubsetParameterization(
                        static_cast<int>(camera->NumParams()), camera_params_const);

                  problem.SetParameterization(camera->ParamsData(), camera_params_parameterization);
               }
            }
         }

         ceres::Solver::Options solver_options;
         solver_options.gradient_tolerance = options.gradient_tolerance;
         solver_options.max_num_iterations = options.max_num_iterations;
         solver_options.linear_solver_type = ceres::DENSE_QR;

         // The overhead of creating threads is too large.
         solver_options.num_threads = 1;
      #if CERES_VERSION_MAJOR < 2
         solver_options.num_linear_solver_threads = 1;
      #endif  // CERES_VERSION_MAJOR

         ceres::Solver::Summary summary;
         ceres::Solve(solver_options, &problem, &summary);

         if (solver_options.minimizer_progress_to_stdout) {
            std::cout << std::endl;
         }

         if (options.print_summary) {
            PrintHeading2("Pose refinement report");
            PrintSolverSummary(summary);
         }

         return summary.IsSolutionUsable();
      }

   .. note::

      函数很长，一点点分析。

      这个函数是通过ceres-Solver进行最小二乘优化，对绝对位姿进行细化。

      1. 定义 LossFunction 为 CauchyLoss。 对 LossFunction 的介绍戳我 |:point_right:|

         .. code-block:: cpp

           ceres::LossFunction* loss_function =  new ceres::CauchyLoss(options.loss_function_scale);

      2. 定义最小二乘解决方法 problem

         .. code-block:: cpp

            ceres::Problem problem;

      3. 定义 CostFunction， 不同的相机模型 影响了 CostFuction里的 :cpp:func: `CameraModel::WorldToImage` 函数

         .. code-block:: cpp

               ceres::CostFunction* cost_function = nullptr;

               switch (camera->ModelId()) {
            #define CAMERA_MODEL_CASE(CameraModel)                                  \
               case CameraModel::kModelId:                                           \
                  cost_function =                                                     \
                     BundleAdjustmentCostFunction<CameraModel>::Create(points2D[i]); \
                  break;

                  CAMERA_MODEL_SWITCH_CASES

            #undef CAMERA_MODEL_CASE
                  }

         这里的 define 后面的 '\\' 实际上是将一行分成了多行去写，指CAMERA_MODEL_CASE实际上定义了后面的一整个case。

         那么这一个switch中，实际上执行的是 ``CAMERA_MODEL_SWITCH_CASES`` 这个宏定义。这个宏在camera_models.h中定义，定义如下：

         .. code-block::

            #ifndef CAMERA_MODEL_SWITCH_CASES
            #define CAMERA_MODEL_SWITCH_CASES         \
               CAMERA_MODEL_CASES                      \
               default:                                \
                  CAMERA_MODEL_DOES_NOT_EXIST_EXCEPTION \
               break;
            #endif

         可以看到， 这个宏执行的是 ``CAMERA_MODEL_CASES`` 这个宏，下面的 ``CAMERA_MODEL_DOES_NOT_EXIST_EXCEPTION`` 是输出错误信息，可以先忽略。

         .. code-block::

            #ifndef CAMERA_MODEL_CASES
            #define CAMERA_MODEL_CASES                          \
              CAMERA_MODEL_CASE(SimplePinholeCameraModel)       \
              CAMERA_MODEL_CASE(PinholeCameraModel)             \
              CAMERA_MODEL_CASE(SimpleRadialCameraModel)        \
              CAMERA_MODEL_CASE(SimpleRadialFisheyeCameraModel) \
              CAMERA_MODEL_CASE(RadialCameraModel)              \
              CAMERA_MODEL_CASE(RadialFisheyeCameraModel)       \
              CAMERA_MODEL_CASE(OpenCVCameraModel)              \
              CAMERA_MODEL_CASE(OpenCVFisheyeCameraModel)       \
              CAMERA_MODEL_CASE(FullOpenCVCameraModel)          \
              CAMERA_MODEL_CASE(FOVCameraModel)                 \
              CAMERA_MODEL_CASE(ThinPrismFisheyeCameraModel)
            #endif

         这下清楚了，最终实际上执行的还是CAMERA_MODEL_CASE(CameraModel)，只是在这个函数里通过宏定义将 ``CAMERA_MODEL_CASE`` 替换成了

         .. code-block:: cpp

            cost_function = BundleAdjustmentCostFunction<CameraModel>::Create(points2D[i]);

      4. 向Problem类传递残差模块的信息，传递的参数主要包括代价函数模块、损失函数模块和参数模块。

         .. code-block:: cpp

            problem.AddResidualBlock(cost_function, loss_function, qvec_data, tvec_data,
                                     points3D_copy[i].data(), camera_params_data);

      5. 设定3D点对应的参数模块在优化过程中保持不变。

         .. code-block:: cpp

            problem.SetParameterBlockConstant(points3D_copy[i].data());

      6. 如果残差的数量 > 0，则：首先进行四元数的参数化。

         这里贴上ceres-Solver对QuaternionParameterization的解释：

         .. math::

            ⊞(x, \Delta) = [cos(|\Delta|, \frac{sin(|\Delta|)}{|\Delta|}\Delta)] * x

         右侧两个四维向量之间的相乘 :math:`*` 是标准四元数乘积。

         .. important::

            ⊞ 符号是指 计算沿 :math:`x` 的切线空间中的增量沿 :math:`\Delta` 移动，然后投影回 :math:`x` 所属的流形的结果。

            通过不同的Parameterization函数来定义不同的 ⊞ :math:`(x, \Delta)` 的含义。

         .. code-block:: cpp

            *qvec = NormalizeQuaternion(*qvec);
            ceres::LocalParameterization* quaternion_parameterization =
               new ceres::QuaternionParameterization;
            problem.SetParameterization(qvec_data, quaternion_parameterization);

         6.1 如果相机不需要优化焦距和外参，则直接将相机的参数设为保持不变

            .. code-block:: cpp

               if (!options.refine_focal_length && !options.refine_extra_params) {
                  problem.SetParameterBlockConstant(camera->ParamsData());
               }

         6.2 否则需要定义一个相机参数序列

            .. code-block:: cpp

               std::vector<int> camera_params_const;

         6.3 通过向这个参数序列中插入 主点的idx，焦距的idx（如果不需要优化焦距），外参的idx（如果不需要优化外参）

            .. code-block:: cpp

               camera_params_const.insert(camera_params_const.end(),
                                 principal_point_idxs.begin(),
                                 principal_point_idxs.end());

               camera_params_const.insert(camera_params_const.end(),
                                   focal_length_idxs.begin(),
                                   focal_length_idxs.end());

               camera_params_const.insert(camera_params_const.end(),
                                   extra_params_idxs.begin(),
                                   extra_params_idxs.end());

         6.4 如果相机的参数数量 = 相机参数序列的参数数量，即都不需要优化（或者是某些参数不存在？），则将相机的参数设为保持不变

            .. code-block:: cpp

               if (camera_params_const.size() == camera->NumParams())
                  problem.SetParameterBlockConstant(camera->ParamsData());

         6.5 否则，即需要进行相机参数的优化，设置 SubsetParameterization

            同样贴上 ceres-Solver的解释：

            假设 :math:`x` 是一个二维向量，并且用户希望保持第一个坐标不变。 那么， :math:`\Delta` 是一个标量， :math:`⊞` 被定义为

            .. math::

               ⊞(x, \Delta) = x + \left[
               \begin{matrix}
               0\\1
               \end{matrix}
               \right]\Delta

            .. code-block:: cpp

               ceres::SubsetParameterization* camera_params_parameterization =
                     new ceres::SubsetParameterization(
                        static_cast<int>(camera->NumParams()), camera_params_const);

               problem.SetParameterization(camera->ParamsData(), camera_params_parameterization);


      7. 设置 Options

         .. code-block:: cpp

            ceres::Solver::Options solver_options;
            solver_options.gradient_tolerance = options.gradient_tolerance;
            solver_options.max_num_iterations = options.max_num_iterations;
            solver_options.linear_solver_type = ceres::DENSE_QR;
            solver_options.num_threads = 1;
            solver_options.num_linear_solver_threads = 1;

      8. 求解最小二乘

         .. code-block:: cpp

            ceres::Solver::Summary summary;
            ceres::Solve(solver_options, &problem, &summary);

RefineRelativePose
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   优化两个相机的相对位姿。

   使用鲁棒的成本函数将对应归一化点之间的Sampson误差最小化，即在给定相对位姿的足够初始猜测的前提下，对应点不一定非是整数。

   假设第一个摄像机位姿具有投影矩阵 :math:`P = [I | 0]` ，第二个摄影机的位姿作为从世界到摄影机系统的转换而给出。

   假设已将给定的位移向量归一化，并将位移精确度提高到未知尺度（即，位移向量进行细化还是单位向量）。

   .. cpp:function:: bool RefineRelativePose(const ceres::Solver::Options& options, const std::vector<Eigen::Vector2d>& points1,const std::vector<Eigen::Vector2d>& points2,Eigen::Vector4d* qvec, Eigen::Vector3d* tvec);

   .. code-block:: cpp

      bool RefineRelativePose(const ceres::Solver::Options& options,
                              const std::vector<Eigen::Vector2d>& points1,
                              const std::vector<Eigen::Vector2d>& points2,
                              Eigen::Vector4d* qvec, Eigen::Vector3d* tvec) {
        CHECK_EQ(points1.size(), points2.size());

        // CostFunction 假定单位四元数
        *qvec = NormalizeQuaternion(*qvec);

        const double kMaxL2Error = 1.0;
        ceres::LossFunction* loss_function = new ceres::CauchyLoss(kMaxL2Error);

        ceres::Problem problem;

        for (size_t i = 0; i < points1.size(); ++i) {
          ceres::CostFunction* cost_function =
              RelativePoseCostFunction::Create(points1[i], points2[i]);
          problem.AddResidualBlock(cost_function, loss_function, qvec->data(),
                                   tvec->data());
        }

        ceres::LocalParameterization* quaternion_parameterization =
            new ceres::QuaternionParameterization;
        problem.SetParameterization(qvec->data(), quaternion_parameterization);

        ceres::HomogeneousVectorParameterization* homogeneous_parameterization =
            new ceres::HomogeneousVectorParameterization(3);
        problem.SetParameterization(tvec->data(), homogeneous_parameterization);

        ceres::Solver::Summary summary;
        ceres::Solve(options, &problem, &summary);

        return summary.IsSolutionUsable();
      }

   .. note::

      整个函数的步骤为：

      1. 单位化四元数

         .. code-block:: cpp

            *qvec = NormalizeQuaternion(*qvec);

      2. 定义 LossFunction， 并设置L2误差最大值为1.0

         .. code-block:: cpp

            const double kMaxL2Error = 1.0;
            ceres::LossFunction* loss_function = new ceres::CauchyLoss(kMaxL2Error);

      3. 定义最小二乘解决方法 problem

         .. code-block:: cpp

            ceres::Problem problem;

      4. 定义 CostFunction 并添加残差模块

         .. code-block:: cpp

            for (size_t i = 0; i < points1.size(); ++i) {
               ceres::CostFunction* cost_function =
                  RelativePoseCostFunction::Create(points1[i], points2[i]);
               problem.AddResidualBlock(cost_function, loss_function, qvec->data(),
                                      tvec->data());
            }

      5. 设置 四元数参数 和 单应性向量参数

         .. code-block:: cpp

            ceres::LocalParameterization* quaternion_parameterization =
               new ceres::QuaternionParameterization;
                  problem.SetParameterization(qvec->data(), quaternion_parameterization);

            ceres::HomogeneousVectorParameterization* homogeneous_parameterization =
               new ceres::HomogeneousVectorParameterization(3);
                  problem.SetParameterization(tvec->data(), homogeneous_parameterization);

      6. 求解最小二乘

         .. code-block:: cpp

            ceres::Solve(options, &problem, &summary);

