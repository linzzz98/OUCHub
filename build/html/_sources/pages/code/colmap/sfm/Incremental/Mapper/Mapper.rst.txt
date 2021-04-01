Incremental_Mapper
============================

为增量重建过程提供所有功能的类

.. important::

   使用方法如下：

   .. code-block:: cpp

      // 构造一个IncrementalMapper，读取数据库的缓存数据（如果有）
      IncrementalMapper mapper(&database_cache);

      // 开始重建
      mapper.BeginReconstruction(&reconstruction);

      // 参数检测
      CHECK(mapper.FindInitialImagePair(options, image_id1, image_id2));
      CHECK(mapper.RegisterInitialImagePair(options, image_id1, image_id2));

      // 增量式重建，循环添加新的图片
      while (...) {

         // 找到下一组添加的图片
         const auto next_image_ids = mapper.FindNextImages(options);

         // 循环添加
         for (const auto image_id : next_image_ids) {
            CHECK(mapper.RegisterNextImage(options, image_id));

            // 局部BA
            if (...) {
               mapper.AdjustLocalBundle(...);
            }

            // 全局BA
            else {
               mapper.AdjustGlobalBundle(...);
            }
         }
      }

      // 结束重建
      mapper.EndReconstruction(false);


.. cpp:class:: IncrementalMapper

配置选项
--------

.. cpp:struct:: IncrementalMapper::Options

.. cpp:member:: int init_min_num_inliers = 100;

   初始图像对的最小inliers数

.. cpp:member:: double init_max_error = 4.0;

   初始图像对的两视图几何估计的最大像素误差

.. cpp:member:: double init_max_forward_motion = 0.95;

   初始图像对的最大前移（Maximum forward motion for initial image pair）

.. cpp:member:: double init_min_tri_angle = 16.0;

   初始图像对的最小三角剖分角

.. cpp:member:: int init_max_reg_trials = 2;

   使用图像进行初始化的最大尝试次数

.. cpp:member:: double abs_pose_max_error = 12.0;

   绝对位姿估计中的最大重投影误差

.. cpp:member:: int abs_pose_min_num_inliers = 30;

   绝对位姿估计中的最小inliers数

.. cpp:member:: double abs_pose_min_inlier_ratio = 0.25;

   绝对位姿估计中的最小inliers比率

.. cpp:member:: bool abs_pose_refine_focal_length = true;

   是否在绝对位姿估计中估计焦距

.. cpp:member:: bool abs_pose_refine_extra_params = true;

   是否在绝对位姿估计中估计额外参数

.. cpp:member:: int local_ba_num_images = 6;

   在局部BA调整中要优化的图像数

.. cpp:member:: double local_ba_min_tri_angle = 6;

   在局部BA调整中选择图像的最小三角剖分

.. cpp:member:: double min_focal_length_ratio = 0.1;
.. cpp:member:: double max_focal_length_ratio = 10;
.. cpp:member:: double max_extra_param = 1;

   伪造相机参数的阈值。 带有伪造相机参数的图像在三角剖分中被过滤并被忽略

.. cpp:member:: double filter_max_reproj_error = 4.0;

   用于观察的最大重投影误差（以像素为单位）

.. cpp:member:: double filter_min_tri_angle = 1.5;

   稳定3D点的最小三角剖分角度（以度为单位）

.. cpp:member:: int max_reg_trials = 3;

   注册图像的最大尝试次数

.. cpp:member:: bool fix_existing_images = false;

   提供重建作为输入，是否修复现存的图像位姿

.. cpp:member:: int num_threads = -1;

   线程数

.. cpp:enum:: ImageSelectionMethod

   查找并选择下一个最佳图像进行注册的方法

   :ImageSelectionMethod:

      * MAX_VISIBLE_POINTS_NUM
      * MAX_VISIBLE_POINTS_RATIO
      * MIN_UNCERTAINTY


结构体
----------------

.. cpp:struct:: LocalBundleAdjustmentReport

.. code-block:: cpp

   struct LocalBundleAdjustmentReport {
      size_t num_merged_observations = 0;
      size_t num_completed_observations = 0;
      size_t num_filtered_observations = 0;
      size_t num_adjusted_observations = 0;
   };



成员变量
-----------------

.. cpp:member:: const DatabaseCache* database_cache_;

   该类将数据库中所有必需的数据保存在内存中

.. cpp:member:: Reconstruction* reconstruction_;

   保存重建数据的类

.. cpp:member:: std::unique_ptr<IncrementalTriangulator> triangulator_;

   负责增量三角剖分的类

.. cpp:member:: size_t num_total_reg_images_;

   至少在重建时注册的图像数量

.. cpp:member:: size_t num_shared_reg_images_;

   当前重建和所有其他先前重建之间共享图像的数量

.. cpp:member:: image_pair_t prev_init_image_pair_id_;

.. cpp:member:: TwoViewGeometry prev_init_two_view_geometry_;

   上一次调用 ``FindFirstInitialImage`` 的估计两视图几何体，用作以后调用 ``RegisterInitialImagePair`` 的缓存。

.. cpp:member:: std::unordered_map<image_t, size_t> init_num_reg_trials_;

.. cpp:member:: std::unordered_set<image_pair_t> init_image_pairs_;

   已用于初始化的图像和图像对。 每个图像和图像对仅尝试一次进行初始化。

.. cpp:member:: std::unordered_map<camera_t, size_t> num_reg_images_per_camera_;

   每个摄像机的已注册图像数。

   当多个图像共享内参时，此信息用于避免重复优化摄像机参数以及在局部BA调整中降低已优化摄像机参数的性能。

.. cpp:member:: std::unordered_map<image_t, size_t> num_registrations_;

   注册图像的重建次数

.. cpp:member:: std::unordered_set<image_t> filtered_images_;

   当前重建中已过滤的图像

.. cpp:member:: std::unordered_map<image_t, size_t> num_reg_trials_;

   在当前重建中注册图像的试验次数。

   用于设置注册图像的尝试次数的上限。

.. cpp:member:: std::unordered_set<image_t> existing_image_ids_;

   开始重建之前已注册的图像。

   如果从现有重建继续进行重建，则此图像列表将为非空。


成员函数
-------------------------

IncrementalMapper
~~~~~~~~~~~~~~~~~~

   构造函数，创建增量映射器。 数据库缓存必须在增量映射器的整个生命周期中都有效。

.. cpp:function:: explicit IncrementalMapper::IncrementalMapper(const DatabaseCache* database_cache);

.. code-block:: cpp

   IncrementalMapper::IncrementalMapper(const DatabaseCache* database_cache)
    : database_cache_(database_cache),
      reconstruction_(nullptr),
      triangulator_(nullptr),
      num_total_reg_images_(0),
      num_shared_reg_images_(0),
      prev_init_image_pair_id_(kInvalidImagePairId) {}


BeginReconstruction
~~~~~~~~~~~~~~~~~~~~~

.. cpp:function:: void IncrementalMapper::BeginReconstruction(Reconstruction* reconstruction)

.. code-block:: cpp

   void IncrementalMapper::BeginReconstruction(Reconstruction* reconstruction) {
      CHECK(reconstruction_ == nullptr);
      reconstruction_ = reconstruction;

      // 从数据库中加载缓存
      reconstruction_->Load(*database_cache_);

      // 开始构建重建
      reconstruction_->SetUp(&database_cache_->CorrespondenceGraph());

      // 设置三角剖分类
      triangulator_.reset(new IncrementalTriangulator(
         &database_cache_->CorrespondenceGraph(), reconstruction));

      num_shared_reg_images_ = 0;
      num_reg_images_per_camera_.clear();

      // 注册图像
      for (const image_t image_id : reconstruction_->RegImageIds()) {
         RegisterImageEvent(image_id);
      }

      // 设置已经存在于重建中的图像id
      existing_image_ids_ =
         std::unordered_set<image_t>(reconstruction->RegImageIds().begin(),
                                     reconstruction->RegImageIds().end());

      // 设置上一次调用indFirstInitialImage的估计两视图几何体的id和两视图几何为空
      prev_init_image_pair_id_ = kInvalidImagePairId;
      prev_init_two_view_geometry_ = TwoViewGeometry();

      filtered_images_.clear();
      num_reg_trials_.clear();
   }

EndRestruction
~~~~~~~~~~~~~~~~~~

   当前重建完成后，清理映射器。

   如果丢弃该模型，则将相应更新总和共享注册图像的数量。

.. cpp:function:: void IncrementalMapper::EndReconstruction(const bool discard)

.. code-block:: cpp

   void IncrementalMapper::EndReconstruction(const bool discard) {
      CHECK_NOTNULL(reconstruction_);

      // 如果丢弃模型
      if (discard) {

         // 解注册图像id
         for (const image_t image_id : reconstruction_->RegImageIds()) {
            DeRegisterImageEvent(image_id);
         }
      }

      // 清理重建映射器
      reconstruction_->TearDown();
      reconstruction_ = nullptr;
      triangulator_.reset();
   }


FindInitialImagePair
~~~~~~~~~~~~~~~~~~~~

   查找初始图像对为增量重建提供种子。 图像对应该传递给 ``RegisterInitialImagePair`` 。

   此函数会自动忽略先前无法注册的图像对。

.. cpp:function:: bool IncrementalMapper::FindInitialImagePair(const Options& options,image_t* image_id1,image_t* image_id2)

.. code-block:: cpp

   bool IncrementalMapper::FindInitialImagePair(const Options& options,
                                                image_t* image_id1,
                                                image_t* image_id2) {
      CHECK(options.Check());

      std::vector<image_t> image_ids1;

      if (*image_id1 != kInvalidImageId && *image_id2 == kInvalidImageId) {

        // 仅提供* image_id1
        if (!database_cache_->ExistsImage(*image_id1)) {
          return false;
        }
        image_ids1.push_back(*image_id1);
      }

      else if (*image_id1 == kInvalidImageId && *image_id2 != kInvalidImageId) {
        // 仅提供* image_id2
        if (!database_cache_->ExistsImage(*image_id2)) {
          return false;
        }
        image_ids1.push_back(*image_id2);
      }

      else {
        // 没有提供初始种子图像
        image_ids1 = FindFirstInitialImage(options);
      }

      // 尝试找到好的初始对
      for (size_t i1 = 0; i1 < image_ids1.size(); ++i1) {
        *image_id1 = image_ids1[i1];

        const std::vector<image_t> image_ids2 =
            FindSecondInitialImage(options, *image_id1);

        for (size_t i2 = 0; i2 < image_ids2.size(); ++i2) {
          *image_id2 = image_ids2[i2];

          const image_pair_t pair_id =
              Database::ImagePairToPairId(*image_id1, *image_id2);

          // 每对仅尝试一次
          if (init_image_pairs_.count(pair_id) > 0) {
            continue;
          }

          init_image_pairs_.insert(pair_id);

          if (EstimateInitialTwoViewGeometry(options, *image_id1, *image_id2)) {
            return true;
          }
        }
      }

      // 在整个数据集中找不到合适的对，返回错误
      *image_id1 = kInvalidImageId;
      *image_id2 = kInvalidImageId;

      return false;
   }

FindFirstInitialImage
~~~~~~~~~~~~~~~~~~~~~~~~~

查找用于增量重建的种子图像。 合适的种子图像具有大量对应关系，并且具有相机校准先验。 返回列表的排序应使最合适的图像位于最前面。

.. cpp:function:: std::vector<image_t> IncrementalMapper::FindFirstInitialImage(const Options& options) const;

.. code-block:: cpp

   std::vector<image_t> IncrementalMapper::FindFirstInitialImage(
       const Options& options) const {

     // 保留元数据（meta-data）以对图像进行排名的结构
     struct ImageInfo {
       image_t image_id;
       bool prior_focal_length;
       image_t num_correspondences;
     };

     const size_t init_max_reg_trials =
         static_cast<size_t>(options.init_max_reg_trials);

     // 收集所有尚未注册的图像的对应信息
     std::vector<ImageInfo> image_infos;
     image_infos.reserve(reconstruction_->NumImages());
     for (const auto& image : reconstruction_->Images()) {
       // 只能注册具有对应关系的图像
       if (image.second.NumCorrespondences() == 0) {
         continue;
       }

       // 图像初始化的次数不能超过规定次数
       if (init_num_reg_trials_.count(image.first) &&
           init_num_reg_trials_.at(image.first) >= init_max_reg_trials) {
         continue;
       }

       // 仅使用未在任何其他重构中注册的图像进行初始化
       if (num_registrations_.count(image.first) > 0 &&
           num_registrations_.at(image.first) > 0) {
         continue;
       }

       const class Camera& camera =
           reconstruction_->Camera(image.second.CameraId());
       ImageInfo image_info;
       image_info.image_id = image.first;
       image_info.prior_focal_length = camera.HasPriorFocalLength();
       image_info.num_correspondences = image.second.NumCorrespondences();
       image_infos.push_back(image_info);
     }

     // 对图像进行排序，使具有优先焦距和更多对应关系的图像成为首选，即它们出现在列表的前面
     std::sort(
         image_infos.begin(), image_infos.end(),
         [](const ImageInfo& image_info1, const ImageInfo& image_info2) {
           if (image_info1.prior_focal_length && !image_info2.prior_focal_length) {
             return true;
           } else if (!image_info1.prior_focal_length &&
                      image_info2.prior_focal_length) {
             return false;
           } else {
             return image_info1.num_correspondences >
                    image_info2.num_correspondences;
           }
         });

     // 按排序顺序提取图像标识符
     std::vector<image_t> image_ids;
     image_ids.reserve(image_infos.size());
     for (const ImageInfo& image_info : image_infos) {
       image_ids.push_back(image_info.image_id);
     }

     return image_ids;
   }

.. note::

   1. 定义一个结构体用于存储图像的id、是否具有先验焦距、对应关系数

      .. code-block:: cpp

         struct ImageInfo {
            image_t image_id;
            bool prior_focal_length;
            image_t num_correspondences;
         };

   2. 定义尝试注册的最大次数

      .. code-block:: cpp

         const size_t init_max_reg_trials = static_cast<size_t>(options.init_max_reg_trials);

   3. 遍历重建中的每张图像，将符合要求的图片加入到 ``image_infos`` 中

      :要求:

         **1. 对应关系** |:heavy_check_mark:|

         .. code-block:: cpp

            if (image.second.NumCorrespondences() == 0) continue;

         **2. 尝试次数少于阈值** |:heavy_check_mark:|

         .. code-block:: cpp

            if (init_num_reg_trials_.count(image.first) &&
                init_num_reg_trials_.at(image.first) >= init_max_reg_trials)

            continue;

         **3. 未在其他重构中注册** |:heavy_check_mark:|

         .. code-block:: cpp

            if (num_registrations_.count(image.first) > 0 &&
                num_registrations_.at(image.first) > 0)

            continue;

   4. 对 ``image_infos`` 中的图片进行排序，使具有优先焦距和更多对应关系的图像成为出现在列表的前面

      .. code-block:: cpp

         std::sort(
            image_infos.begin(), image_infos.end(),
            [](const ImageInfo& image_info1, const ImageInfo& image_info2) {

               if (image_info1.prior_focal_length && !image_info2.prior_focal_length)
                  return true;

               else if (!image_info1.prior_focal_length && image_info2.prior_focal_length)
                  return false;

               else
                  return image_info1.num_correspondences > image_info2.num_correspondences;
         });

   5. 按排序顺序提取图像标识符（id）

      .. code-block:: cpp

         for (const ImageInfo& image_info : image_infos)
            image_ids.push_back(image_info.image_id);

FindSecondInitialImage
~~~~~~~~~~~~~~~~~~~~~~~

.. cpp:function:: std::vector<image_t> IncrementalMapper::FindSecondInitialImage(const Options& options, const image_t image_id1) const;

.. code-block:: cpp

   std::vector<image_t> IncrementalMapper::FindSecondInitialImage(
       const Options& options, const image_t image_id1) const {
     const CorrespondenceGraph& correspondence_graph =
         database_cache_->CorrespondenceGraph();

     // 收集连接到第一个种子图像且之前未在其他重建中注册的图像
     const class Image& image1 = reconstruction_->Image(image_id1);
     std::unordered_map<image_t, point2D_t> num_correspondences;
     for (point2D_t point2D_idx = 0; point2D_idx < image1.NumPoints2D();
          ++point2D_idx) {
       for (const auto& corr :
            correspondence_graph.FindCorrespondences(image_id1, point2D_idx)) {
         if (num_registrations_.count(corr.image_id) == 0 ||
             num_registrations_.at(corr.image_id) == 0) {
           num_correspondences[corr.image_id] += 1;
         }
       }
     }

     // 保留元数据（meta-data）以对图像进行排名的结构
     struct ImageInfo {
       image_t image_id;
       bool prior_focal_length;
       point2D_t num_correspondences;
     };

     const size_t init_min_num_inliers =
         static_cast<size_t>(options.init_min_num_inliers);

     // 以紧凑的形式组合图像信息以进行分类
     std::vector<ImageInfo> image_infos;
     image_infos.reserve(reconstruction_->NumImages());

     for (const auto elem : num_correspondences) {
       // 如果点的数量大于最小内点数
       if (elem.second >= init_min_num_inliers) {
         const class Image& image = reconstruction_->Image(elem.first);
         const class Camera& camera = reconstruction_->Camera(image.CameraId());
         ImageInfo image_info;
         image_info.image_id = elem.first;
         image_info.prior_focal_length = camera.HasPriorFocalLength();
         image_info.num_correspondences = elem.second;
         image_infos.push_back(image_info);
       }
     }

     // 对图像进行排序，使具有优先焦距和更多对应关系的图像成为首选，即它们出现在列表的前面
     std::sort(
         image_infos.begin(), image_infos.end(),
         [](const ImageInfo& image_info1, const ImageInfo& image_info2) {
           if (image_info1.prior_focal_length && !image_info2.prior_focal_length) {
             return true;
           } else if (!image_info1.prior_focal_length &&
                      image_info2.prior_focal_length) {
             return false;
           } else {
             return image_info1.num_correspondences >
                    image_info2.num_correspondences;
           }
         });

     // 按排序顺序提取图像标识符
     std::vector<image_t> image_ids;
     image_ids.reserve(image_infos.size());
     for (const ImageInfo& image_info : image_infos) {
       image_ids.push_back(image_info.image_id);
     }

     return image_ids;
   }

.. note::

   1. 定义一个结构体用于存储图像的id、是否具有先验焦距、对应关系数

      .. code-block:: cpp

         struct ImageInfo {
            image_t image_id;
            bool prior_focal_length;
            image_t num_correspondences;
         };

   2. 得到内存缓存中的关系图

      .. code-block:: cpp

         const CorrespondenceGraph& correspondence_graph = database_cache_->CorrespondenceGraph();

   3. 遍历图1中的每一个特征点，每个特征点都对应许多的图，如果对应的图没有被注册到其他重建中，则将图的id作为 ``num_correspondences`` 的下标+1，记录该图与图1的关联性

      .. code-block:: cpp

         const class Image& image1 = reconstruction_->Image(image_id1);
         std::unordered_map<image_t, point2D_t> num_correspondences;
         for (point2D_t point2D_idx = 0; point2D_idx < image1.NumPoints2D();
             ++point2D_idx) {
            for (const auto& corr :
               correspondence_graph.FindCorrespondences(image_id1, point2D_idx)) {
               if (num_registrations_.count(corr.image_id) == 0 ||
                num_registrations_.at(corr.image_id) == 0) {
                  num_correspondences[corr.image_id] += 1;
               }
            }
         }

   4. 遍历与图1有关联的所有的图，如果图的特征点数量大于内点阈值，则将其加入到 ``image_infos`` 中

      .. code-block:: cpp

         std::vector<ImageInfo> image_infos;
         image_infos.reserve(reconstruction_->NumImages());
         for (const auto elem : num_correspondences) {
            if (elem.second >= init_min_num_inliers) {
               const class Image& image = reconstruction_->Image(elem.first);
               const class Camera& camera = reconstruction_->Camera(image.CameraId());
               ImageInfo image_info;
               image_info.image_id = elem.first;
               image_info.prior_focal_length = camera.HasPriorFocalLength();
               image_info.num_correspondences = elem.second;
               image_infos.push_back(image_info);
            }
         }

   5. 对 ``image_infos`` 中的图片进行排序，使具有优先焦距和更多对应关系的图像成为出现在列表的前面

      .. code-block:: cpp

         std::sort(
            image_infos.begin(), image_infos.end(),
            [](const ImageInfo& image_info1, const ImageInfo& image_info2) {
               if (image_info1.prior_focal_length && !image_info2.prior_focal_length)
                  return true;

               else if (!image_info1.prior_focal_length && image_info2.prior_focal_length)
                  return false;
               else
                return image_info1.num_correspondences > image_info2.num_correspondences;
            });

   6. 按排序顺序提取图像标识符（id）

      .. code-block:: cpp

         for (const ImageInfo& image_info : image_infos) {
            image_ids.push_back(image_info.image_id);
         }

FindNextImages
~~~~~~~~~~~~~~~

查找最佳的下一组图像以注册到增量重建。

图像应传递到 ``RegisterNextImag``。 此函数会自动忽略未注册 ``max_reg_trial`` 的图像。

.. cpp:function:: std::vector<image_t> IncrementalMapper::FindNextImages(const Options& options);

.. code-block:: cpp

   std::vector<image_t> IncrementalMapper::FindNextImages(const Options& options) {
      CHECK_NOTNULL(reconstruction_);
      CHECK(options.Check());


      std::function<float(const Image&)> rank_image_func;

      // 根据method决定选择下一张图像的函数
      switch (options.image_selection_method) {
        case Options::ImageSelectionMethod::MAX_VISIBLE_POINTS_NUM:
          rank_image_func = RankNextImageMaxVisiblePointsNum;
          break;
        case Options::ImageSelectionMethod::MAX_VISIBLE_POINTS_RATIO:
          rank_image_func = RankNextImageMaxVisiblePointsRatio;
          break;
        case Options::ImageSelectionMethod::MIN_UNCERTAINTY:
          rank_image_func = RankNextImageMinUncertainty;
          break;
      }

      std::vector<std::pair<image_t, float>> image_ranks;
      std::vector<std::pair<image_t, float>> other_image_ranks;

      // 附加之前没有失败注册的图像
      for (const auto& image : reconstruction_->Images()) {
        // 跳过已注册的图像
        if (image.second.IsRegistered()) {
          continue;
        }

        // 仅考虑具有足够数量的可见点的图像
        if (image.second.NumVisiblePoints3D() <
            static_cast<size_t>(options.abs_pose_min_num_inliers)) {
          continue;
        }

        // 只尝试注册最大次数
        const size_t num_reg_trials = num_reg_trials_[image.first];
        if (num_reg_trials >= static_cast<size_t>(options.max_reg_trials)) {
          continue;
        }

        // 如果图像已被过滤或注册失败，将其放置在第二个存储桶中，并优先使用之前未尝试过的图像。
        const float rank = rank_image_func(image.second);
        if (filtered_images_.count(image.first) == 0 && num_reg_trials == 0) {
          image_ranks.emplace_back(image.first, rank);
        } else {
          other_image_ranks.emplace_back(image.first, rank);
        }
      }

      std::vector<image_t> ranked_images_ids;
      SortAndAppendNextImages(image_ranks, &ranked_images_ids);
      SortAndAppendNextImages(other_image_ranks, &ranked_images_ids);

      return ranked_images_ids;
   }

.. note::

   1. 注意 ``std::function<float(const Image&)> rank_image_func`` 实际上类似一个指针函数，代码中设置了三种不同的方法：

         1） 根据可见点数量

            .. code-block:: cpp

               float RankNextImageMaxVisiblePointsNum(const Image& image)
                  return static_cast<float>(image.NumVisiblePoints3D());

         2） 根据可见点的比率

            .. code-block:: cpp

               float RankNextImageMaxVisiblePointsRatio(const Image& image) {
                  return static_cast<float>(image.NumVisiblePoints3D()) /
                        static_cast<float>(image.NumObservations());
               }

         3） 根据得分金字塔

            .. code-block:: cpp

               float RankNextImageMinUncertainty(const Image& image) {
                  return static_cast<float>(image.Point3DVisibilityScore());
               }

      2.  ``SortAndAppendNextImages`` 是根据上一步图像的得分对图像进行排序，并加入新的图像进去。

            .. code-block:: cpp

               void SortAndAppendNextImages(std::vector<std::pair<image_t, float>> image_ranks,
                             std::vector<image_t>* sorted_images_ids) {
                  std::sort(image_ranks.begin(), image_ranks.end(),
                           [](const std::pair<image_t, float>& image1,
                              const std::pair<image_t, float>& image2) {
                             return image1.second > image2.second;
                           });

                  sorted_images_ids->reserve(sorted_images_ids->size() + image_ranks.size());
                  for (const auto& image : image_ranks) {
                     sorted_images_ids->push_back(image.first);
                  }

                  image_ranks.clear();
               }


EstimateInitialTwoViewGeometry
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

估计初始种子图像对的两视图几何

.. cpp:function:: bool IncrementalMapper::EstimateInitialTwoViewGeometry(const Options& options, const image_t image_id1, const image_t image_id2)

.. code-block:: cpp

   bool IncrementalMapper::EstimateInitialTwoViewGeometry(
       const Options& options, const image_t image_id1, const image_t image_id2) {

      // 根据图像id得到图像对
      const image_pair_t image_pair_id =
         Database::ImagePairToPairId(image_id1, image_id2);

      if (prev_init_image_pair_id_ == image_pair_id) {
         return true;
      }

      // 得到图像、对应相机、关联图、匹配关系
      const Image& image1 = database_cache_->Image(image_id1);
      const Camera& camera1 = database_cache_->Camera(image1.CameraId());

      const Image& image2 = database_cache_->Image(image_id2);
      const Camera& camera2 = database_cache_->Camera(image2.CameraId());

      const CorrespondenceGraph& correspondence_graph =
         database_cache_->CorrespondenceGraph();
      const FeatureMatches matches =
         correspondence_graph.FindCorrespondencesBetweenImages(image_id1,
                                                               image_id2);

      // 将图1中的特征点加入points1
      std::vector<Eigen::Vector2d> points1;
      points1.reserve(image1.NumPoints2D());
      for (const auto& point : image1.Points2D()) {
         points1.push_back(point.XY());
      }

      // 将图2中的特征点加入points2
      std::vector<Eigen::Vector2d> points2;
      points2.reserve(image2.NumPoints2D());
      for (const auto& point : image2.Points2D()) {
         points2.push_back(point.XY());
      }

      // 两视图几何估计
      TwoViewGeometry two_view_geometry;
      TwoViewGeometry::Options two_view_geometry_options;
      two_view_geometry_options.ransac_options.min_num_trials = 30;
      two_view_geometry_options.ransac_options.max_error = options.init_max_error;
      two_view_geometry.EstimateCalibrated(camera1, points1, camera2, points2,
                                          matches, two_view_geometry_options);

      // 估计两视图相对位姿
      if (!two_view_geometry.EstimateRelativePose(camera1, points1, camera2,
                                                 points2)) {
         return false;
      }

      // 如果匹配内点数 > 最小初始化内点数 且 z轴移动 < 最大位移 且 三角剖分角 > 最小三角剖分角，则估计成功
      if (static_cast<int>(two_view_geometry.inlier_matches.size()) >=
          options.init_min_num_inliers &&
          std::abs(two_view_geometry.tvec.z()) < options.init_max_forward_motion &&
          two_view_geometry.tri_angle > DegToRad(options.init_min_tri_angle)) {
            prev_init_image_pair_id_ = image_pair_id;
            prev_init_two_view_geometry_ = two_view_geometry;
            return true;
      }

      return false;
   }

RegisterInitialImagePair
~~~~~~~~~~~~~~~~~~~~~~~~

从种子图像对开始重建

.. cpp:function:: bool IncrementalMapper::RegisterInitialImagePair(const Options& options,const image_t image_id1,const image_t image_id2)

.. code-block:: cpp

   bool IncrementalMapper::RegisterInitialImagePair(const Options& options,
                                                    const image_t image_id1,
                                                    const image_t image_id2) {
      CHECK_NOTNULL(reconstruction_);
      CHECK_EQ(reconstruction_->NumRegImages(), 0);

      CHECK(options.Check());

      init_num_reg_trials_[image_id1] += 1;
      init_num_reg_trials_[image_id2] += 1;
      num_reg_trials_[image_id1] += 1;
      num_reg_trials_[image_id2] += 1;

      // 得到图像对
      const image_pair_t pair_id =
            Database::ImagePairToPairId(image_id1, image_id2);
      init_image_pairs_.insert(pair_id);

      // 得到图像和对应相机
      Image& image1 = reconstruction_->Image(image_id1);
      const Camera& camera1 = reconstruction_->Camera(image1.CameraId());

      Image& image2 = reconstruction_->Image(image_id2);
      const Camera& camera2 = reconstruction_->Camera(image2.CameraId());

      //////////////////////////////////////////////////////////////////////////////
      // 估计两视图几何
      //////////////////////////////////////////////////////////////////////////////

      if (!EstimateInitialTwoViewGeometry(options, image_id1, image_id2)) {
         return false;
      }

      // 设第一个图像的旋转为单位矩阵，位移为零向量
      image1.Qvec() = ComposeIdentityQuaternion();
      image1.Tvec() = Eigen::Vector3d(0, 0, 0);

      // 第二个图像的R和t为从两视图几何中分解得到的相对旋转和位移
      image2.Qvec() = prev_init_two_view_geometry_.qvec;
      image2.Tvec() = prev_init_two_view_geometry_.tvec;

      // 得到两个图像的投影矩阵和投影中心
      const Eigen::Matrix3x4d proj_matrix1 = image1.ProjectionMatrix();
      const Eigen::Matrix3x4d proj_matrix2 = image2.ProjectionMatrix();
      const Eigen::Vector3d proj_center1 = image1.ProjectionCenter();
      const Eigen::Vector3d proj_center2 = image2.ProjectionCenter();

      //////////////////////////////////////////////////////////////////////////////
      // 更新重建
      //////////////////////////////////////////////////////////////////////////////

      // 重建注册两个图片
      reconstruction_->RegisterImage(image_id1);
      reconstruction_->RegisterImage(image_id2);
      RegisterImageEvent(image_id1);
      RegisterImageEvent(image_id2);

      // 从数据库中得到关联图和特征匹配
      const CorrespondenceGraph& correspondence_graph =
            database_cache_->CorrespondenceGraph();
      const FeatureMatches& corrs =
            correspondence_graph.FindCorrespondencesBetweenImages(image_id1,
                                                               image_id2);

      // 得到最小三角剖分角度
      const double min_tri_angle_rad = DegToRad(options.init_min_tri_angle);

      // 将3D点加入到Track中
      Track track;
      track.Reserve(2);
      track.AddElement(TrackElement());
      track.AddElement(TrackElement());
      track.Element(0).image_id = image_id1;
      track.Element(1).image_id = image_id2;

      // 遍历所有的匹配点
      for (const auto& corr : corrs) {
         // 将两幅图的特征匹配点从图像坐标系变换到世界坐标系
         const Eigen::Vector2d point1_N =
            camera1.ImageToWorld(image1.Point2D(corr.point2D_idx1).XY());
         const Eigen::Vector2d point2_N =
            camera2.ImageToWorld(image2.Point2D(corr.point2D_idx2).XY());

         // 三角化匹配点，得到3D点
         const Eigen::Vector3d& xyz =
            TriangulatePoint(proj_matrix1, proj_matrix2, point1_N, point2_N);

         // 根据投影矩阵和3D点计算三角剖分角
         const double tri_angle =
            CalculateTriangulationAngle(proj_center1, proj_center2, xyz);

         // 如果三角剖分角 >= 最小三角剖分角度， 且投影之后的3D点的深度为正，则将该3D点加入重建
         if (tri_angle >= min_tri_angle_rad &&
            HasPointPositiveDepth(proj_matrix1, xyz) &&
            HasPointPositiveDepth(proj_matrix2, xyz)) {
            track.Element(0).point2D_idx = corr.point2D_idx1;
            track.Element(1).point2D_idx = corr.point2D_idx2;
            reconstruction_->AddPoint3D(xyz, track);
         }
      }

      return true;
   }

RegisterNextImage
~~~~~~~~~~~~~~~~~

尝试将图像注册到现有模型。

要求之前对 ``RegisterInitialImagePair`` 的调用成功。

.. cpp:function:: bool IncrementalMapper::RegisterNextImage(const Options& options, const image_t image_id)

.. code-block:: cpp

   bool IncrementalMapper::RegisterNextImage(const Options& options,
                                             const image_t image_id) {
     CHECK_NOTNULL(reconstruction_);
     CHECK_GE(reconstruction_->NumRegImages(), 2);

     CHECK(options.Check());

      // 得到图片和对应相机
      Image& image = reconstruction_->Image(image_id);
      Camera& camera = reconstruction_->Camera(image.CameraId());

      CHECK(!image.IsRegistered()) << "Image cannot be registered multiple times";

      // 该图片的尝试注册次数+1
      num_reg_trials_[image_id] += 1;

      // 如果没有足够多的可见点，则注册失败
      if (image.NumVisiblePoints3D() <
            static_cast<size_t>(options.abs_pose_min_num_inliers)) {
         return false;
      }

      //////////////////////////////////////////////////////////////////////////////
      // 寻找2D-3D对应关系
      //////////////////////////////////////////////////////////////////////////////

      const int kCorrTransitivity = 1;

      std::vector<std::pair<point2D_t, point3D_t>> tri_corrs;
      std::vector<Eigen::Vector2d> tri_points2D;
      std::vector<Eigen::Vector3d> tri_points3D;

      for (point2D_t point2D_idx = 0; point2D_idx < image.NumPoints2D();
            ++point2D_idx) {
         const Point2D& point2D = image.Point2D(point2D_idx);
         const CorrespondenceGraph& correspondence_graph =
            database_cache_->CorrespondenceGraph();

         // kCorrTransitivity = 1 相当于找到对应的匹配点对
         const std::vector<CorrespondenceGraph::Correspondence> corrs =
            correspondence_graph.FindTransitiveCorrespondences(
                  image_id, point2D_idx, kCorrTransitivity);

         std::unordered_set<point3D_t> point3D_ids;

         // 遍历所有的特征点对
         for (const auto corr : corrs) {
            const Image& corr_image = reconstruction_->Image(corr.image_id);

            // 如果该对应图像没有被注册，则跳过
            if (!corr_image.IsRegistered()) {
               continue;
            }

            const Point2D& corr_point2D = corr_image.Point2D(corr.point2D_idx);
            if (!corr_point2D.HasPoint3D()) {
               continue;
            }

            // Avoid duplicate correspondences.
            if (point3D_ids.count(corr_point2D.Point3DId()) > 0) {
               continue;
            }

            const Camera& corr_camera =
               reconstruction_->Camera(corr_image.CameraId());

            // 避免与伪造的相机参数对应的图像
            if (corr_camera.HasBogusParams(options.min_focal_length_ratio,
                                        options.max_focal_length_ratio,
                                        options.max_extra_param)) {
               continue;
            }

            const Point3D& point3D =
               reconstruction_->Point3D(corr_point2D.Point3DId());

            tri_corrs.emplace_back(point2D_idx, corr_point2D.Point3DId());
            point3D_ids.insert(corr_point2D.Point3DId());
            tri_points2D.push_back(point2D.XY());
            tri_points3D.push_back(point3D.XYZ());
         }
      }

      // The size of `next_image.num_tri_obs` and `tri_corrs_point2D_idxs.size()`
      // can only differ, when there are images with bogus camera parameters, and
      // hence we skip some of the 2D-3D correspondences.
      if (tri_points2D.size() <
            static_cast<size_t>(options.abs_pose_min_num_inliers)) {
         return false;
      }

      //////////////////////////////////////////////////////////////////////////////
      // 2D-3D 估计
      //////////////////////////////////////////////////////////////////////////////

      // 如果未指定焦距（手动或通过EXIF）并且先前尚未从其他图像进行估计（当多个图像共享相同的相机参数时），则仅优化/估计焦距。

      AbsolutePoseEstimationOptions abs_pose_options;
      abs_pose_options.num_threads = options.num_threads;
      abs_pose_options.num_focal_length_samples = 30;
      abs_pose_options.min_focal_length_ratio = options.min_focal_length_ratio;
      abs_pose_options.max_focal_length_ratio = options.max_focal_length_ratio;
      abs_pose_options.ransac_options.max_error = options.abs_pose_max_error;
      abs_pose_options.ransac_options.min_inlier_ratio =
            options.abs_pose_min_inlier_ratio;
      // Use high confidence to avoid preemptive termination of P3P RANSAC
      // - too early termination may lead to bad registration.
      abs_pose_options.ransac_options.min_num_trials = 100;
      abs_pose_options.ransac_options.max_num_trials = 10000;
      abs_pose_options.ransac_options.confidence = 0.99999;

      AbsolutePoseRefinementOptions abs_pose_refinement_options;
      if (num_reg_images_per_camera_[image.CameraId()] > 0) {
         // Camera already refined from another image with the same camera.
         if (camera.HasBogusParams(options.min_focal_length_ratio,
                                    options.max_focal_length_ratio,
                                    options.max_extra_param)) {
            // Previously refined camera has bogus parameters,
            // so reset parameters and try to re-estimage.
            camera.SetParams(database_cache_->Camera(image.CameraId()).Params());
            abs_pose_options.estimate_focal_length = !camera.HasPriorFocalLength();
            abs_pose_refinement_options.refine_focal_length = true;
            abs_pose_refinement_options.refine_extra_params = true;
         } else {
            abs_pose_options.estimate_focal_length = false;
            abs_pose_refinement_options.refine_focal_length = false;
            abs_pose_refinement_options.refine_extra_params = false;
         }
      } else {
         // Camera not refined before. Note that the camera parameters might have
         // been changed before but the image was filtered, so we explicitly reset
         // the camera parameters and try to re-estimate them.
         camera.SetParams(database_cache_->Camera(image.CameraId()).Params());
         abs_pose_options.estimate_focal_length = !camera.HasPriorFocalLength();
         abs_pose_refinement_options.refine_focal_length = true;
         abs_pose_refinement_options.refine_extra_params = true;
      }

      if (!options.abs_pose_refine_focal_length) {
         abs_pose_options.estimate_focal_length = false;
         abs_pose_refinement_options.refine_focal_length = false;
      }

      if (!options.abs_pose_refine_extra_params) {
         abs_pose_refinement_options.refine_extra_params = false;
      }

      size_t num_inliers;
      std::vector<char> inlier_mask;

      if (!EstimateAbsolutePose(abs_pose_options, tri_points2D, tri_points3D,
                                 &image.Qvec(), &image.Tvec(), &camera, &num_inliers,
                                 &inlier_mask)) {
         return false;
      }

      if (num_inliers < static_cast<size_t>(options.abs_pose_min_num_inliers)) {
         return false;
      }

     //////////////////////////////////////////////////////////////////////////////
     // Pose refinement
     //////////////////////////////////////////////////////////////////////////////

      if (!RefineAbsolutePose(abs_pose_refinement_options, inlier_mask,
                              tri_points2D, tri_points3D, &image.Qvec(),
                              &image.Tvec(), &camera)) {
         return false;
      }

     //////////////////////////////////////////////////////////////////////////////
     // Continue tracks
     //////////////////////////////////////////////////////////////////////////////

      reconstruction_->RegisterImage(image_id);
      RegisterImageEvent(image_id);

      for (size_t i = 0; i < inlier_mask.size(); ++i) {
         if (inlier_mask[i]) {
            const point2D_t point2D_idx = tri_corrs[i].first;
            const Point2D& point2D = image.Point2D(point2D_idx);
            if (!point2D.HasPoint3D()) {
               const point3D_t point3D_id = tri_corrs[i].second;
               const TrackElement track_el(image_id, point2D_idx);
               reconstruction_->AddObservation(point3D_id, track_el);
               triangulator_->AddModifiedPoint3D(point3D_id);
            }
         }
      }

      return true;
   }
