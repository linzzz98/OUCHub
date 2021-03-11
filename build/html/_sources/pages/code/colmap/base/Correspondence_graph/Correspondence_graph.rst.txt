.. default-domain:: cpp

Correspondence\_graph
=====================

场景图表示数据集的图像与图像以及特征与特征的对应关系的图。
应该从DatabaseCache访问它。

.. warning::

    该页没做完，以后再做

结构体
~~~~~~~~~

.. cpp:struct Correspondence

.. cpp:type:: uint32_t colmap::image_t

.. cpp:type:: uint32_t colmap::point2D_t

.. code-block:: cpp

    struct Correspondence {

        Correspondence() : image_id(kInvalidImageId), point2D_idx(kInvalidPoint2DIdx) {}

        Correspondence(const image_t image_id, const point2D_t point2D_idx) : image_id(image_id), point2D_idx(point2D_idx) {}

        // 对应图像的标识
        // typedef uint32_t colmap::image_t
        image_t image_id;

        // 对应图像中相应点的索引
        point2D_t point2D_idx;
        };
    };

.. cpp:struct Image

.. code-block:: cpp

    struct Image {
        // 与另一张图片至少具有一个对应关系的2D点的数量
        point2D_t num_observations = 0;

        // 与其他图像的对应总数。 对于找到一个良好的初始对很有用，该初始对连接到许多图像
        point2D_t num_correspondences = 0;

        // 每个图像点与其他图像的对应关系
        std::vector<std::vector<Correspondence>> corrs;
    };

.. cpp:struct ImagePair

.. code-block:: cpp

    struct ImagePair {
        // 图像对之间的对应数
        point2D_t num_correspondences = 0;
    };

成员函数
~~~~~~~~~~~~~~~~~~

1. 数量

* 添加的图像的数量

    .. cpp:function:: inline size_t NumImages() const;

* 添加的图像对数量

    .. cpp:function:: inline size_t NumImagePairs() const;

* 图像中的observations。 observation是具有至少一个对应关系的图像点

    .. cpp:function:: inline point2D_t NumObservationsForImage(const image_t image_id) const;

* 获取每个图像的对应数量 inline point2D_t

    .. cpp:function:: NumCorrespondencesForImage(const image_t image_id) const;

* 获取一对图像之间的对应数 inline point2D_t

    .. cpp:function:: NumCorrespondencesBetweenImages(const image_t image_id1, const image_t image_id2) const;

* 获取所有图像之间的对应数量

    .. cpp:function:: std::unordered_mapNumCorrespondencesBetweenImages() const;

2. 数据库管理器

（1）通过计算至少具有一种对应关系的图像点的数量，计算每幅图像的观察次数。

（2）删除没有观察结果的图像，因为它们对SfM无用。

（3）将对应向量shrink\_to\_fit以节省内存。

.. code-block:: cpp

    void CorrespondenceGraph::Finalize() {

      for (auto it = images_.begin(); it != images_.end();) {

        it->second.num_observations = 0;

        for (auto& corr : it->second.corrs) {

          // 缩小对应向量的大小至当前容量
          corr.shrink_to_fit();

          if (corr.size() > 0)
            it->second.num_observations += 1;
        }

        if (it->second.num_observations == 0)
          images_.erase(it++);

        else
          ++it;
      }
    }

3. 添加新的图片到关联图中

.. cpp:function:: void AddImage(const image_t image_id, const size_t num_points2D);

在图像之间添加对应关系

.. cpp:function:: void AddCorrespondences(const image_t image_id1, const image_t image_id2, const FeatureMatches& matches);

4. 查找

查找图像观察值与所有其他图像的对应关系

.. cpp:function:: inline const std::vector<Correspondence>& FindCorrespondences(const image_t image_id, const point2D_t point2D_idx) const;

查找与给定观察值的对应关系

.. cpp:function:: std::vector<Correspondence> FindTransitiveCorrespondences(const image_t image_id, const point2D_t point2D_idx,const size_t transitivity) const;

找到两个图像之间所有的对应

.. cpp:function:: FeatureMatches FindCorrespondencesBetweenImages(const image_t image_id1, const image_t image_id2) const;
