TwoViewGeometry
=================

结构体
-------

.. cpp:struct:: TwoViewGeometry

.. cpp:enum:: ConfigurationType

   :UNDEFINED = 0:

      未定义

   :DEGENERATE = 1:

      退化的配置（如没有重叠或没有足够多的内点）

   :CALIBRATED = 2:

      本质矩阵

   :UNCALIBRATED = 3:

      基础矩阵

   :PLANAR = 4:

      单应性，带有基线的平面场景

   :PANORAMIC = 5:

      单应性，无基线的纯旋转

   :PLANAR_OR_PANORAMIC = 6:

      平面或全景的单应性

   :WATERMARK = 7:

      水印，图像边界中的纯2D转换

   :MULTIPLE = 8:

      多模型配置，（内点的匹配来自多个单独的，非退化的配置）

配置
-----------

.. cpp:struct:: Options

:size_t min_num_inliers = 15:

   非退化两视图几何的最小内点数

:double min_E_F_inlier_ratio = 0.95:

   如果两个摄像机都已校准，则可通过估计基本矩阵和基本矩阵并比较其像素数量的分数来验证校准。

   如果基本矩阵产生相似数量的inlier（`min_E_F_inlier_ratio * F_num_inliers`），则认为校准是正确的。

:double max_H_inlier_ratio = 0.8:

   如果可以验证对极几何，检查该几何是否描述了单应性描述的平面场景或全景视图（纯旋转）。

   这是一个退化的情况，因为对极几何仅定义在移动的相机上。

   如果单应性的inlier比率接近对极几何的inlier比率，则假定其为平面（带有基线的平面场景）或全景（无基线的纯旋转）配置。

:double watermark_min_inlier_ratio = 0.7:

   在有效的两视图几何情况下，检查几何图形是否在图像的边界区域中描述了纯平移。

   如果超过一定比例的内点与纯图像平移相符，则假定其为水印。

:double watermark_border_size = 0.1:

   水印匹配必须在图像的边界区域中。

   边界区域定义为图像边界周围的区域，并定义为图像对角线的一小部分。

:bool detect_watermark = true:

   是否启用水印检测。

   水印会在图像空间中产生纯平移，并且边界区域中会包含内点。

:bool multiple_ignore_watermark = true:

   在多模型估计中是否忽略水印模型。

:RANSACOptions ransac_options:

   用于鲁棒估计几何形状的选项。

成员变量
-----------

1. 配置类型

   .. cpp:member:: int config;

2. 本质矩阵

   .. cpp:member:: Eigen::Matrix3d E;

3. 基础矩阵

   .. cpp:member:: Eigen::Matrix3d F;

4. 单应矩阵

   .. cpp:member:: Eigen::Matrix3d H;

5. 相对位姿

   .. cpp:member:: Eigen::Vector4d qvec;

   .. cpp:member:: Eigen::Vector3d tvec;

6. 配置的内点匹配

   .. cpp:member:: FeatureMatches inlier_matches;

7. 三角剖分中位角

   .. cpp:member:: double tri_angle;

成员函数
-----------

Invert
~~~~~~~

   反转两视图几何

.. cpp:function:: void TwoViewGeometry::Invert()

.. code-block:: cpp

   void TwoViewGeometry::Invert() {
      F.transposeInPlace();
      E.transposeInPlace();
      H = H.inverse().eval();

      const Eigen::Vector4d orig_qvec = qvec;
      const Eigen::Vector3d orig_tvec = tvec;
      InvertPose(orig_qvec, orig_tvec, &qvec, &tvec);

      for (auto& match : inlier_matches) {
         std::swap(match.point2D_idx1, match.point2D_idx2);
      }
   }

.. note::

   1. 在Eigen里，如果让一个矩阵 = 其转置，则

      .. math::

         A = A.transpose()

      这种表达是错误的，必须使用

      .. math::

         a.transposeInPlace();

   2. 交换两视图位姿

      .. code-block:: cpp

         InvertPose(orig_qvec, orig_tvec, &qvec, &tvec);

      **InvertPose**

      .. code-block:: cpp

         void InvertPose(const Eigen::Vector4d& qvec, const Eigen::Vector3d& tvec,
                         Eigen::Vector4d* inv_qvec, Eigen::Vector3d* inv_tvec) {
           *inv_qvec = InvertQuaternion(qvec);
           *inv_tvec = -QuaternionRotatePoint(*inv_qvec, tvec);
         }

      **InvertQuaternion**

      .. code-block:: cpp

         Eigen::Vector4d InvertQuaternion(const Eigen::Vector4d& qvec) {
            return Eigen::Vector4d(qvec(0), -qvec(1), -qvec(2), -qvec(3));
         }

      **QuaternionRotatePoint**

      .. code-block:: cpp

         Eigen::Vector3d QuaternionRotatePoint(const Eigen::Vector4d& qvec,
                                               const Eigen::Vector3d& point) {
            const Eigen::Vector4d normalized_qvec = NormalizeQuaternion(qvec);
            const Eigen::Quaterniond quat(normalized_qvec(0), normalized_qvec(1),
                                         normalized_qvec(2), normalized_qvec(3));
            return quat * point;
         }


Estimate
~~~~~~~~~~

   根据已给定或未给定的焦距，从已校准或未校准的图像对估计两视图几何形状。

   .. cpp:function:: void TwoViewGeometry::Estimate(const Camera& camera1,const std::vector<Eigen::Vector2d>& points1,const Camera& camera2,const std::vector<Eigen::Vector2d>& points2,const FeatureMatches& matches,const Options& options)

   .. code-block:: cpp

      void TwoViewGeometry::Estimate(const Camera& camera1,
                                     const std::vector<Eigen::Vector2d>& points1,
                                     const Camera& camera2,
                                     const std::vector<Eigen::Vector2d>& points2,
                                     const FeatureMatches& matches,
                                     const Options& options) {
         if (camera1.HasPriorFocalLength() && camera2.HasPriorFocalLength()) {
            EstimateCalibrated(camera1, points1, camera2, points2, matches, options);
         } else {
            EstimateUncalibrated(camera1, points1, camera2, points2, matches, options);
         }
      }


EstimateMultiple
~~~~~~~~~~~~~~~~~~~~

   通过从匹配中不断删除之前的一组内点，直到找不到足够多的内点，来递归估计多个配置。

   如果可以估计多个模型，则串联内点的匹配，并且配置类型为“ MULTIPLE”。 这对于估计场景中具有较大失真或多个刚性移动对象的图像的两视图几何结构很有用。

   请注意，如果模型类型为“ MULTIPLE”，则只会初始化“ inlier_matches”字段。

   .. cpp:function:: void TwoViewGeometry::EstimateMultiple(const Camera& camera1, const std::vector<Eigen::Vector2d>& points1,const Camera& camera2, const std::vector<Eigen::Vector2d>& points2,const FeatureMatches& matches, const Options& options)

   .. code-block:: cpp

      void TwoViewGeometry::EstimateMultiple(
          const Camera& camera1, const std::vector<Eigen::Vector2d>& points1,
          const Camera& camera2, const std::vector<Eigen::Vector2d>& points2,
          const FeatureMatches& matches, const Options& options) {
        FeatureMatches remaining_matches = matches;
        std::vector<TwoViewGeometry> two_view_geometries;
        while (true) {
          TwoViewGeometry two_view_geometry;
          two_view_geometry.Estimate(camera1, points1, camera2, points2,
                                     remaining_matches, options);
          if (two_view_geometry.config == ConfigurationType::DEGENERATE) {
            break;
          }

          if (options.multiple_ignore_watermark) {
            if (two_view_geometry.config != ConfigurationType::WATERMARK) {
              two_view_geometries.push_back(two_view_geometry);
            }
          } else {
            two_view_geometries.push_back(two_view_geometry);
          }

          // 不断删除内点，留下外点进行迭代
          remaining_matches = ExtractOutlierMatches(remaining_matches,
                                                    two_view_geometry.inlier_matches);
        }

        if (two_view_geometries.empty()) {
          config = ConfigurationType::DEGENERATE;
        } else if (two_view_geometries.size() == 1) {
          *this = two_view_geometries[0];
        } else {
          config = ConfigurationType::MULTIPLE;

          for (const auto& two_view_geometry : two_view_geometries) {
            inlier_matches.insert(inlier_matches.end(),
                                  two_view_geometry.inlier_matches.begin(),
                                  two_view_geometry.inlier_matches.end());
          }
        }
      }



EstimateCalibrated
~~~~~~~~~~~~~~~~~~~~

   从校准的图像对中估计两视图几何形状

   .. cpp:function:: void TwoViewGeometry::EstimateCalibrated(const Camera& camera1, const std::vector<Eigen::Vector2d>& points1,const Camera& camera2, const std::vector<Eigen::Vector2d>& points2,const FeatureMatches& matches, const Options& options)

   .. code-block:: cpp

      void TwoViewGeometry::EstimateCalibrated(
            const Camera& camera1, const std::vector<Eigen::Vector2d>& points1,
            const Camera& camera2, const std::vector<Eigen::Vector2d>& points2,
            const FeatureMatches& matches, const Options& options) {
         options.Check();

         // 匹配数过少
         if (matches.size() < options.min_num_inliers) {
            config = ConfigurationType::DEGENERATE;
            return;
         }

         // 提取相应的点
         std::vector<Eigen::Vector2d> matched_points1(matches.size());
         std::vector<Eigen::Vector2d> matched_points2(matches.size());
         std::vector<Eigen::Vector2d> matched_points1_normalized(matches.size());
         std::vector<Eigen::Vector2d> matched_points2_normalized(matches.size());
         for (size_t i = 0; i < matches.size(); ++i) {
            const point2D_t idx1 = matches[i].point2D_idx1;
            const point2D_t idx2 = matches[i].point2D_idx2;
            matched_points1[i] = points1[idx1];
            matched_points2[i] = points2[idx2];
            matched_points1_normalized[i] = camera1.ImageToWorld(points1[idx1]);
            matched_points2_normalized[i] = camera2.ImageToWorld(points2[idx2]);
         }

         // 估计对极几何模型

         auto E_ransac_options = options.ransac_options;
         E_ransac_options.max_error =
               (camera1.ImageToWorldThreshold(options.ransac_options.max_error) +
               camera2.ImageToWorldThreshold(options.ransac_options.max_error)) / 2;

         LORANSAC<EssentialMatrixFivePointEstimator, EssentialMatrixFivePointEstimator>
               E_ransac(E_ransac_options);
         const auto E_report =
               E_ransac.Estimate(matched_points1_normalized, matched_points2_normalized);
         E = E_report.model;

         LORANSAC<FundamentalMatrixSevenPointEstimator,
                  FundamentalMatrixEightPointEstimator>
               F_ransac(options.ransac_options);
         const auto F_report = F_ransac.Estimate(matched_points1, matched_points2);
         F = F_report.model;

        // 估计 平面 还是 全景模型

         LORANSAC<HomographyMatrixEstimator, HomographyMatrixEstimator> H_ransac(
            options.ransac_options);
         const auto H_report = H_ransac.Estimate(matched_points1, matched_points2);
         H = H_report.model;

         if ((!E_report.success && !F_report.success && !H_report.success) ||
            (E_report.support.num_inliers < options.min_num_inliers &&
             F_report.support.num_inliers < options.min_num_inliers &&
             H_report.support.num_inliers < options.min_num_inliers)) {
            config = ConfigurationType::DEGENERATE;
            return;
         }

         // 决定不同模型之间的内点比率

         const double E_F_inlier_ratio =
            static_cast<double>(E_report.support.num_inliers) /
            F_report.support.num_inliers;
         const double H_F_inlier_ratio =
            static_cast<double>(H_report.support.num_inliers) /
            F_report.support.num_inliers;
         const double H_E_inlier_ratio =
            static_cast<double>(H_report.support.num_inliers) /
            E_report.support.num_inliers;

         const std::vector<char>* best_inlier_mask = nullptr;
         size_t num_inliers = 0;

         if (E_report.success && E_F_inlier_ratio > options.min_E_F_inlier_ratio &&
            E_report.support.num_inliers >= options.min_num_inliers) {
          // 标定配置

          // 使用有最大匹配数的模型
          if (E_report.support.num_inliers >= F_report.support.num_inliers) {
            num_inliers = E_report.support.num_inliers;
            best_inlier_mask = &E_report.inlier_mask;
          }
         else {
            num_inliers = F_report.support.num_inliers;
            best_inlier_mask = &F_report.inlier_mask;
          }

          if (H_E_inlier_ratio > options.max_H_inlier_ratio) {
               config = PLANAR_OR_PANORAMIC;
               if (H_report.support.num_inliers > num_inliers) {
                  num_inliers = H_report.support.num_inliers;
                  best_inlier_mask = &H_report.inlier_mask;
               }
          }
         else
               config = ConfigurationType::CALIBRATED;

         }

         else if (F_report.success &&
                   F_report.support.num_inliers >= options.min_num_inliers) {
          // 未标定配置

          num_inliers = F_report.support.num_inliers;
          best_inlier_mask = &F_report.inlier_mask;

          if (H_F_inlier_ratio > options.max_H_inlier_ratio) {
            config = ConfigurationType::PLANAR_OR_PANORAMIC;
            if (H_report.support.num_inliers > num_inliers) {
              num_inliers = H_report.support.num_inliers;
              best_inlier_mask = &H_report.inlier_mask;
            }
          } else {
            config = ConfigurationType::UNCALIBRATED;
          }
        } else if (H_report.success &&
                   H_report.support.num_inliers >= options.min_num_inliers) {
          num_inliers = H_report.support.num_inliers;
          best_inlier_mask = &H_report.inlier_mask;
          config = ConfigurationType::PLANAR_OR_PANORAMIC;
        } else {
          config = ConfigurationType::DEGENERATE;
          return;
        }

        if (best_inlier_mask != nullptr) {
          inlier_matches =
              ExtractInlierMatches(matches, num_inliers, *best_inlier_mask);

          if (options.detect_watermark &&
              DetectWatermark(camera1, matched_points1, camera2, matched_points2,
                              num_inliers, *best_inlier_mask, options)) {
            config = ConfigurationType::WATERMARK;
          }
        }
      }

   .. note::

      :算法步骤:

         1. 提取匹配特征点
         2. 估计 :math:`E,F,H` 矩阵
         3. 计算不同模型之间的内点比率 :math:`EF,HF,HE`
         4. 根据内点比率判断是标定模型、未标点模型、平面/全景模型、退化模型
         5. 内点遮罩过滤
         6. 水印检测


EstimateUncalibrated
~~~~~~~~~~~~~~~~~~~~~~~~

   从未校准的图像对估计两视图几何形状。

   .. cpp:function:: void TwoViewGeometry::EstimateUncalibrated(const Camera& camera1, const std::vector<Eigen::Vector2d>& points1,const Camera& camera2, const std::vector<Eigen::Vector2d>& points2,const FeatureMatches& matches, const Options& options)

   .. code-block:: cpp

      void TwoViewGeometry::EstimateUncalibrated(
          const Camera& camera1, const std::vector<Eigen::Vector2d>& points1,
          const Camera& camera2, const std::vector<Eigen::Vector2d>& points2,
          const FeatureMatches& matches, const Options& options) {
        options.Check();

        if (matches.size() < options.min_num_inliers) {
          config = ConfigurationType::DEGENERATE;
          return;
        }

        // 提取特征匹配点
        std::vector<Eigen::Vector2d> matched_points1(matches.size());
        std::vector<Eigen::Vector2d> matched_points2(matches.size());
        for (size_t i = 0; i < matches.size(); ++i) {
          matched_points1[i] = points1[matches[i].point2D_idx1];
          matched_points2[i] = points2[matches[i].point2D_idx2];
        }

        // 估计对极几何模型

        LORANSAC<FundamentalMatrixSevenPointEstimator,
                 FundamentalMatrixEightPointEstimator>
            F_ransac(options.ransac_options);
        const auto F_report = F_ransac.Estimate(matched_points1, matched_points2);
        F = F_report.model;

        // 估计 平面 还是 全景模型

        LORANSAC<HomographyMatrixEstimator, HomographyMatrixEstimator> H_ransac(
            options.ransac_options);
        const auto H_report = H_ransac.Estimate(matched_points1, matched_points2);
        H = H_report.model;

        if ((!F_report.success && !H_report.success) ||
            (F_report.support.num_inliers < options.min_num_inliers &&
             H_report.support.num_inliers < options.min_num_inliers)) {
          config = ConfigurationType::DEGENERATE;
          return;
        }

        // 决定不同模型之间的内点比率

        const double H_F_inlier_ratio =
            static_cast<double>(H_report.support.num_inliers) /
            F_report.support.num_inliers;

        if (H_F_inlier_ratio > options.max_H_inlier_ratio) {
          config = ConfigurationType::PLANAR_OR_PANORAMIC;
        } else {
          config = ConfigurationType::UNCALIBRATED;
        }

        // 内点遮罩提取内点匹配

        inlier_matches = ExtractInlierMatches(matches, F_report.support.num_inliers,
                                              F_report.inlier_mask);

        // 检测水印
        if (options.detect_watermark &&
            DetectWatermark(camera1, matched_points1, camera2, matched_points2,
                            F_report.support.num_inliers, F_report.inlier_mask,
                            options)) {
          config = ConfigurationType::WATERMARK;
        }
      }

   .. note::

      :算法步骤:

         1. 提取匹配特征点（与Calibrated不同的是，因为不需要估计 :math:`E` 矩阵，所以不需要归一化点）
         2. 估计 :math:`F,H` 矩阵
         3. 计算不同模型之间的内点比率 :math:`HF`
         4. 根据内点比率判断是未标定、平面/全景模型、退化模型
         5. 内点遮罩过滤
         6. 水印检测


DetectWatermark
~~~~~~~~~~~~~~~~~~

   检测内部匹配是否由水印引起。
   水印会导致图像边框的纯平移。

   .. cpp:function:: bool TwoViewGeometry::DetectWatermark(const Camera& camera1, const std::vector<Eigen::Vector2d>& points1,const Camera& camera2, const std::vector<Eigen::Vector2d>& points2,const size_t num_inliers, const std::vector<char>& inlier_mask,const Options& options)

   .. code-block:: cpp

      bool TwoViewGeometry::DetectWatermark(
            const Camera& camera1, const std::vector<Eigen::Vector2d>& points1,
            const Camera& camera2, const std::vector<Eigen::Vector2d>& points2,
            const size_t num_inliers, const std::vector<char>& inlier_mask,
            const Options& options) {
         options.Check();

         // 检查边界区域是否有内点，并提取内点匹配对

         // 两视图对角线长度
         const double diagonal1 = std::sqrt(camera1.Width() * camera1.Width() +
                                           camera1.Height() * camera1.Height());
         const double diagonal2 = std::sqrt(camera2.Width() * camera2.Width() +
                                           camera2.Height() * camera2.Height());
         const double minx1 = options.watermark_border_size * diagonal1;
         const double miny1 = minx1;
         const double maxx1 = camera1.Width() - minx1;
         const double maxy1 = camera1.Height() - miny1;
         const double minx2 = options.watermark_border_size * diagonal2;
         const double miny2 = minx2;
         const double maxx2 = camera2.Width() - minx2;
         const double maxy2 = camera2.Height() - miny2;

         std::vector<Eigen::Vector2d> inlier_points1(num_inliers);
         std::vector<Eigen::Vector2d> inlier_points2(num_inliers);

         size_t num_matches_in_border = 0;

         size_t j = 0;
         for (size_t i = 0; i < inlier_mask.size(); ++i) {
            if (inlier_mask[i]) {
               const auto& point1 = points1[i];
               const auto& point2 = points2[i];

               inlier_points1[j] = point1;
               inlier_points2[j] = point2;
               j += 1;

               if (!IsImagePointInBoundingBox(point1, minx1, maxx1, miny1, maxy1) &&
                  !IsImagePointInBoundingBox(point2, minx2, maxx2, miny2, maxy2)) {
               num_matches_in_border += 1;
               }
            }
         }

         const double matches_in_border_ratio =
               static_cast<double>(num_matches_in_border) / num_inliers;

         if (matches_in_border_ratio < options.watermark_min_inlier_ratio) {
            return false;
         }

         // 检查匹配是否遵循位移模型

         RANSACOptions ransac_options = options.ransac_options;
         ransac_options.min_inlier_ratio = options.watermark_min_inlier_ratio;

         LORANSAC<TranslationTransformEstimator<2>, TranslationTransformEstimator<2>>
               ransac(ransac_options);
         const auto report = ransac.Estimate(inlier_points1, inlier_points2);

         const double inlier_ratio =
               static_cast<double>(report.support.num_inliers) / num_inliers;

         return inlier_ratio >= options.watermark_min_inlier_ratio;
      }

   .. cpp:function:: inline bool IsImagePointInBoundingBox(const Eigen::Vector2d& point,const double minx, const double maxx,const double miny, const double maxy)

   .. code-block:: cpp

      inline bool IsImagePointInBoundingBox(const Eigen::Vector2d& point,
                                            const double minx, const double maxx,
                                            const double miny, const double maxy) {
        return point.x() >= minx && point.x() <= maxx && point.y() >= miny &&
               point.y() <= maxy;
      }

