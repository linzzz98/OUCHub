Reconstrucion
=================

重构类保存有关单个重构模型的所有信息。

.. cpp:class:: Reconstruction

.. cpp:struct:: ImagePairStat

   :ImagePairStat:

      .. cpp:member:: size_t num_tri_corrs = 0;

         两个图像之间的三角对应关系数

      .. cpp:member:: size_t num_total_corrs = 0;

         两个图像之间的总对应/匹配数

内联函数
----------------

**获取对象数**

   .. code-block:: cpp

      inline size_t NumCameras() const;

      inline size_t NumImages() const;

      inline size_t NumRegImages() const;

      inline size_t NumPoints3D() const;

      inline size_t NumImagePairs() const;

**获取常量对象**

   .. code-block:: cpp

      inline const class Camera& Camera(const camera_t camera_id) const;

      inline const class Image& Image(const image_t image_id) const;

      inline const class Point3D& Point3D(const point3D_t point3D_id) const;

      inline const ImagePairStat& ImagePair(const image_pair_t pair_id) const;

      inline ImagePairStat& ImagePair(const image_t image_id1,const image_t image_id2);

**获取可变对象**

   .. code-block:: cpp

      inline class Camera& Camera(const camera_t camera_id);

      inline class Image& Image(const image_t image_id);

      inline class Point3D& Point3D(const point3D_t point3D_id);

      inline ImagePairStat& ImagePair(const image_pair_t pair_id);

      inline const ImagePairStat& ImagePair(const image_t image_id1,
                                        const image_t image_id2) const;


**获取对所有对象的引用**

   .. code-block:: cpp

      inline const EIGEN_STL_UMAP(camera_t, class Camera) & Cameras() const;

      inline const EIGEN_STL_UMAP(image_t, class Image) & Images() const;

      inline const std::vector<image_t>& RegImageIds() const;

      inline const EIGEN_STL_UMAP(point3D_t, class Point3D) & Points3D() const;

      inline const std::unordered_map<image_pair_t, ImagePairStat>& ImagePairs() const;

**所有3D点的标识符**

   .. code-block:: cpp

      std::unordered_set<point3D_t> Point3DIds() const;

**检查特定对象是否存在**

   .. code-block:: cpp

      inline bool ExistsCamera(const camera_t camera_id) const;

      inline bool ExistsImage(const image_t image_id) const;

      inline bool ExistsPoint3D(const point3D_t point3D_id) const;

      inline bool ExistsImagePair(const image_pair_t pair_id) const;

成员变量
-------------

成员函数
-------------

SetUp
~~~~~~~

   重建之前设置所有相关的数据结构

   .. cpp:function:: void Reconstruction::SetUp(const CorrespondenceGraph* correspondence_graph)

   .. code-block:: cpp

      void Reconstruction::SetUp(const CorrespondenceGraph* correspondence_graph) {
         CHECK_NOTNULL(correspondence_graph);
         for (auto& image : images_) {
            image.second.SetUp(Camera(image.second.CameraId()));
         }
         correspondence_graph_ = correspondence_graph;

        // 如果从磁盘加载了现有模型，并且之前已经注册了图像，则需要将观测值设置为三角测量
         for (const auto image_id : reg_image_ids_) {
            const class Image& image = Image(image_id);
            for (point2D_t point2D_idx = 0; point2D_idx < image.NumPoints2D();
                  ++point2D_idx) {
               if (image.Point2D(point2D_idx).HasPoint3D()) {
               const bool kIsContinuedPoint3D = false;
               SetObservationAsTriangulated(image_id, point2D_idx,
                                           kIsContinuedPoint3D);
               }
            }
         }
      }

