.. default-domain:: cpp

Image
=====

包含有关图像信息的类。
如果一个图像的内参相同，则它可能与其他多个图像共享一个相机。

成员变量
~~~~~~~~

1. 图片的标识符

.. cpp:member:: image_t image_id_;

2. 图片名称，即相对路径

.. cpp:member:: std::string name_;

3. 关联摄像机的标识符。 请注意，多个图像可能共享同一台摄像机。

.. cpp:member:: camera_t camera_id_;

4. 图像是否在重建中成功配准

.. cpp:member:: bool registered_;

5. 图像观察到的3D点的数量，即其“ points2D”的总和

.. cpp:member:: point2D_t num_points3D_;

6. 与另一张图像具有至少一个对应关系的图像点的数量

.. cpp:member:: point2D_t num_observations_;

7. 每个图像点的对应关系之和

.. cpp:member:: point2D_t num_correspondences_;

8. 2D点的数量，在另一个图像中至少有一个对应的2D点是3D点轨迹的一部分，即“
   points2D”的总和

.. cpp:member:: point2D_t num_visible_points3D_;

9. 图像的位姿，定义为从世界坐标系到图像坐标系的转换

.. cpp:member:: Eigen::Vector4d qvec_;

.. cpp:member:: Eigen::Vector3d tvec_;

10. 所有图像点，包括不属于3D点轨迹的点

.. cpp:member:: std::vector<class Point2D> points2D_;

11. 每个图像点对应的3D点的数量

.. cpp:member:: std::vector<image_t> num_correspondences_have_point3D_;

12. 用于计算图像中三角对应关系的分布

.. cpp:member:: VisibilityPyramid point3D_visibility_pyramid_;

成员函数
~~~~~~~~

1. 在重建之前和之后设置/拆除图像和必要的内部数据结构。

.. code-block:: cpp

    void Image::SetUp(const class Camera& camera) {
      CHECK_EQ(camera_id_, camera.CameraId());

      // 设置可见点金字塔：kNumPoint3DVisibilityPyramidLevels = 6
      point3D_visibility_pyramid_ = VisibilityPyramid(
          kNumPoint3DVisibilityPyramidLevels, camera.Width(), camera.Height());
    }

    void Image::TearDown() {
      // 将可见点金字塔归0
      point3D_visibility_pyramid_ = VisibilityPyramid(0, 0, 0);
    }

2. 访问图像的唯一标识符

.. cpp:function:: inline image_t ImageId() const;

.. cpp:function:: inline void SetImageId(const image_t image_id);

3. 访问图像的名称

.. cpp:function:: inline const std::string& Name() const;

.. cpp:function:: inline std::string& Name();

.. cpp:function:: inline void SetName(const std::string& name);

4. 访问摄像机的唯一标识符。（多个图像可能共享同一台相机）

.. cpp:function:: inline camera_t CameraId() const;

.. cpp:function:: inline void SetCameraId(const camera_t camera_id);

.. cpp:function:: inline bool HasCamera() const;


5. 图像是否被配准

.. cpp:function:: inline bool IsRegistered() const;
.. cpp:function:: inline void SetRegistered(const bool registered);

6. 数量

* 获取图像点的数量。

    .. cpp:function:: inline point2D_t NumPoints2D() const;

* 获取三角化的数量，即3D点轨迹中的点的数量。
    .. cpp:function:: inline point2D_t NumPoints3D() const;

* 获取观测值的数量，即与另一个图像至少具有一个对应关系的图像点的数量。

    .. cpp:function:: inline point2D_t NumObservations() const;

    .. cpp:function:: inline void SetNumObservations(const point2D_t num_observations);

* 获取所有图像对应点的数量

    .. cpp:function:: inline point2D_t NumCorrespondences() const;

    .. cpp:function:: inline void SetNumCorrespondences(const point2D_t num_observations);

* 获取看到三角化点的观测值的数量，即与另一幅图像中的三角化点至少具有一个对应关系的图像点的数量。

    .. cpp:function:: inline point2D_t NumVisiblePoints3D() const;


7. 3D点的得分

获取三角测量的分数。 与“NumVisiblePoints3D”相反，该得分还捕获了三角观测值在图像中的分布。

.. cpp:function:: inline size_t Point3DVisibilityScore() const;

8. 四元数向量，

访问四元数向量为（qw，qx，qy，qz），用于指定位姿的旋转，该旋转定义为从世界到图像空间的转换。

.. cpp:function:: inline const Eigen::Vector4d& Qvec() const;

.. cpp:function:: inline Eigen::Vector4d& Qvec();

.. cpp:function:: inline double Qvec(const size_t idx) const;

.. cpp:function:: inline double& Qvec(const size_t idx);

.. cpp:function:: inline void SetQvec(const Eigen::Vector4d& qvec);

访问四元数向量为（tx，ty，tz），用于指定位姿的平移，该位姿的平移定义为从世界到图像空间的转换。

.. cpp:function:: inline const Eigen::Vector3d& Tvec() const;

.. cpp:function:: inline Eigen::Vector3d& Tvec();

.. cpp:function:: inline double Tvec(const size_t idx) const;

.. cpp:function:: inline double& Tvec(const size_t idx);

.. cpp:function:: inline void SetTvec(const Eigen::Vector3d& tvec);

规范四元数向量

.. cpp:function:: void NormalizeQvec();

9. 点的坐标

访问图像点的坐标

.. cpp:function:: inline const class Point2D& Point2D(const point2D_t point2D_idx) const;

.. cpp:function:: inline class Point2D& Point2D(const point2D_t point2D_idx);

.. cpp:function:: inline const std::vector<class Point2D>& Points2D() const;

.. code-block:: cpp

    void Image::SetPoints2D(const std::vector<Eigen::Vector2d>& points) {
      CHECK(points2D_.empty());
      points2D_.resize(points.size());
      num_correspondences_have_point3D_.resize(points.size(), 0);
      for (point2D_t point2D_idx = 0; point2D_idx < points.size(); ++point2D_idx) {
        points2D_[point2D_idx].SetXY(points[point2D_idx]);
      }
    }

    void Image::SetPoints2D(const std::vector<class Point2D>& points) {
      CHECK(points2D_.empty());
      points2D_ = points;
      num_correspondences_have_point3D_.resize(points.size(), 0);
    }

将点设置为3D点track的一部分

.. cpp:function:: void Image::ResetPoint3DForPoint2D(const point2D_t point2D_idx);

.. code-block:: cpp

    void Image::SetPoint3DForPoint2D(const point2D_t point2D_idx,
                                     const point3D_t point3D_id) {
      CHECK_NE(point3D_id, kInvalidPoint3DId);
      class Point2D& point2D = points2D_.at(point2D_idx);
      if (!point2D.HasPoint3D()) {
        num_points3D_ += 1;
      }
      point2D.SetPoint3DId(point3D_id);
    }

将点设置为不属于3D点track

.. cpp:function:: void Image::ResetPoint3DForPoint2D(const point2D_t point2D_idx) const;

.. code-block:: cpp

    void Image::ResetPoint3DForPoint2D(const point2D_t point2D_idx) {
      class Point2D& point2D = points2D_.at(point2D_idx);
      if (point2D.HasPoint3D()) {
        point2D.SetPoint3DId(kInvalidPoint3DId);
        num_points3D_ -= 1;
      }
    }

检查一个图像点是否与另一个具有3D点的图像中的一个图像点相对应

.. cpp:function:: inline bool IsPoint3DVisible(const point2D_t point2D_idx) const;

检查其中一个图像点是否属于3D点track

.. cpp:function:: bool Image::HasPoint3D(const point3D_t point3D_id) const;

.. code-block:: cpp

    bool Image::HasPoint3D(const point3D_t point3D_id) const {
      return std::find_if(points2D_.begin(), points2D_.end(),
                          [point3D_id](const class Point2D& point2D) {
                            return point2D.Point3DId() == point3D_id;
                          }) != points2D_.end();
    }


指示另一个图像具有三角剖分的点，并且与该图像点具有对应关系

.. cpp:function:: void Image::IncrementCorrespondenceHasPoint3D(const point2D_t point2D_idx);

.. code-block:: cpp

    void Image::IncrementCorrespondenceHasPoint3D(const point2D_t point2D_idx) {
      const class Point2D& point2D = points2D_.at(point2D_idx);

      num_correspondences_have_point3D_[point2D_idx] += 1;
      if (num_correspondences_have_point3D_[point2D_idx] == 1) {
        num_visible_points3D_ += 1;
      }

      point3D_visibility_pyramid_.SetPoint(point2D.X(), point2D.Y());

      assert(num_visible_points3D_ <= num_observations_);
    }


指示另一个图像的点不再被三角剖分，并且与该图像点具有对应关系

.. cpp:function:: void Image::DecrementCorrespondenceHasPoint3D(const point2D_t point2D_idx);

.. code-block:: cpp

    void Image::DecrementCorrespondenceHasPoint3D(const point2D_t point2D_idx) {
      const class Point2D& point2D = points2D_.at(point2D_idx);

      num_correspondences_have_point3D_[point2D_idx] -= 1;
      if (num_correspondences_have_point3D_[point2D_idx] == 0) {
        num_visible_points3D_ -= 1;
      }

      point3D_visibility_pyramid_.ResetPoint(point2D.X(), point2D.Y());

      assert(num_visible_points3D_ <= num_observations_);
    }


10. 矩阵

* 组成从世界到图像空间的投影矩阵

    .. cpp:function:: Eigen::Matrix3x4d ProjectionMatrix() const;

* 组成从图像到世界空间的逆投影矩阵

    .. cpp:function:: Eigen::Matrix3x4d InverseProjectionMatrix() const;

* 根据四元数向量组成旋转矩阵

    .. cpp:function:: Eigen::Matrix3d RotationMatrix() const;

* 将投影中心提取到世界空间中

    .. cpp:function:: Eigen::Vector3d ProjectionCenter() const;

* 提取图像的视图方向

    .. cpp:function:: Eigen::Vector3d ViewingDirection() const;


