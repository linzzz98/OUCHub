.. default-domain:: cpp

Camera
======

colmap的camera文件共分为：

* camera

* camera\_models

* camera\_database

* camera\_rig

Camera\_Models
~~~~~~~~~~~~~~~~~

该文件定义了几种不同的摄像机型号，也可以添加任意新的摄像机型号。

相机模型可以具有三种不同类型的相机参数：焦距，主点，额外参数(失真参数)。参数数组分为不同的组，因此可以在BA调整期间启用或禁用单个组的优化。

相机模型必须具有以下方法：

-  ``WorldToImage``\ ：将标准化的摄影机坐标转换为图像坐标(与ImageToWorld相反)。
   假设世界坐标为(u，v，1)。
-  ``ImageToWorld``\ ：将图像坐标转换为标准化的摄影机坐标(与WorldToImage相反)。
   产生世界坐标为(u，v，1)。
-  ``ImageToWorldThreshold``\ ：将以像素为单位的阈值转换为归一化的单位(对于重投影误差阈值很有用)。

(每当列表中指定摄像机参数时，它们必须按照在定义的模型结构中访问它们时的顺序准确显示。)

摄像机模型遵循以下约定：图像左上角的坐标为(0，0)，右下角的坐标为(width，height)，即左上像素中心的坐标为(0.5，0.5)，右下像素中心的坐标为(宽度-0.5，高度-0.5)。

--------------

不同的相机模型
^^^^^^^^^^^^^^

+--------------------------------------+--------------------------------------------------------------------+------------+----------------------------------------------------+
| 模型                                 | 描述                                                               | 参数数量   | 参数列表排列顺序                                   |
+======================================+====================================================================+============+====================================================+
| ``SimplePinholeCameraModel``         | 没有失真。 仅对焦距和主要点进行建模                                | 3          | f, cx, cy                                          |
+--------------------------------------+--------------------------------------------------------------------+------------+----------------------------------------------------+
| ``PinholeCameraModel``               | 没有失真。 仅对焦距和主要点进行建模                                | 4          | fx, fy, cx, cy                                     |
+--------------------------------------+--------------------------------------------------------------------+------------+----------------------------------------------------+
| ``SimpleRadialCameraModel``          | 具有一个焦距和一个径向失真参数的简单相机模型                       | 4          | f, cx, cy, k                                       |
+--------------------------------------+--------------------------------------------------------------------+------------+----------------------------------------------------+
| ``RadialCameraModel``                | 具有一个焦距和两个径向变形参数的简单相机模型                       | 5          | f, cx, cy, k1, k2                                  |
+--------------------------------------+--------------------------------------------------------------------+------------+----------------------------------------------------+
| ``OpenCVCameraModel``                | 基于针孔相机模型，不适用于鱼眼镜头较大径向变形                     | 8          | fx, fy, cx, cy, k1, k2, p1, p2                     |
+--------------------------------------+--------------------------------------------------------------------+------------+----------------------------------------------------+
| ``OpenCVFisheyeCameraModel``         | 基于针孔相机模型，适用于鱼眼镜头较大径向变形                       | 8          | fx, fy, cx, cy, k1, k2, k3, k4                     |
+--------------------------------------+--------------------------------------------------------------------+------------+----------------------------------------------------+
| ``FullOpenCVCameraModel``            | 基于针孔相机模型。可以模拟径向和切向变形                           | 12         | fx, fy, cx, cy, k1, k2, p1, p2, k3, k4, k5, k6     |
+--------------------------------------+--------------------------------------------------------------------+------------+----------------------------------------------------+
| ``FOVCameraModel``                   | 基于针孔相机模型。 可以对径向变形进行建模                          | 5          | fx, fy, cx, cy, omega                              |
+--------------------------------------+--------------------------------------------------------------------+------------+----------------------------------------------------+
| ``SimpleRadialFisheyeCameraModel``   | 具有一个焦距和一个径向失真参数的简单相机模型，适用于鱼眼镜头相机   | 4          | f, cx, cy, k                                       |
+--------------------------------------+--------------------------------------------------------------------+------------+----------------------------------------------------+
| ``ThinPrismFisheyeCameraModel``      | 具有径向和切向畸变系数以及其他系数的相机模型                       | 12         | fx, fy, cx, cy, k1, k2, p1, p2, k3, k4, sx1, sy1   |
+--------------------------------------+--------------------------------------------------------------------+------------+----------------------------------------------------+

**SIMPLE\_PINHOLE，PINHOLE**\ ：如果图像没有先验失真，请使用这些相机型号。它们分别使用一个和两个焦距参数。请注意，即使在图像不失真的情况下，COLMAP仍可以尝试使用更复杂的相机模型来改善内在性。

**SIMPLE\_RADIAL，RADIAL**\ ：如果内参未知且每个图像都有不同的相机校准(例如，对于Internet照片)，则应该选择该相机模型。这两个模型都是OPENCV模型的简化版本，仅分别使用一个和两个参数对径向变形效果进行建模。

**OPENCV，FULL\_OPENCV**\ ：如果事先知道内参，请使用这些相机型号。如果共享多个图像的内在函数，则还可以尝试让COLMAP估计参数。请注意，如果每个图像都有一组单独的固有参数，则参数的自动估计很可能会失败。

**SIMPLE\_RADIAL\_FISHEYE，RADIAL\_FISHEYE，OPENCV\_FISHEYE，FOV和THIN\_PRISM\_FISHEYE**\ ：将这些相机模型用于鱼眼镜头，请注意，其他所有模型都无法真正模拟鱼眼镜头的畸变效果。
Google Project Tango使用FOV模型(请确保不要将omega初始化为零)。

相关函数
^^^^^^^^

-  根据相机id和名字找到对应的名字和id

.. cpp:function:: int CameraModelNameToId(const std::string& model_name);

.. cpp:function:: std::string CameraModelIdToName(const int model_id);

-  使用给定的参数初始化相机参数

.. cpp:function:: std::vector<double> CameraModelInitializeParams(const int model_id, const double focal_length, const size_t width, const size_t height);

-  获取参数向量中参数组的索引

colmap通过不同的数组存储对应的焦距，主点，和其他参数。通过相机id进行查找。

.. cpp:function:: const std::vector<size_t>& CameraModelFocalLengthIdxs(const int model_id);

.. cpp:function:: const std::vector<size_t>& CameraModelPrincipalPointIdxs(const int model_id);

.. cpp:function:: const std::vector<size_t>& CameraModelExtraParamsIdxs(const int model_id);

-  将以像素为单位的阈值转换为归一化的单位

.. code-block:: cpp

    template <typename CameraModel>

    template <typename T>

    T BaseCameraModel<CameraModel>::ImageToWorldThreshold(const T* params, const T threshold){

    T mean_focal_length = 0;

    for (const auto& idx : CameraModel::focal_length_idxs) {

        mean_focal_length += params[idx];}

        mean_focal_length /= CameraModel::focal_length_idxs.size();

        return threshold / mean_focal_length;   }

-  以SimpleRadialCameraModel为例(colmap默认相机模型参数为SimpleRadialCameraModel)：

.. figure:: 1.png
    :figclass: align-center

1. 将标准化的摄影机坐标转换为图像坐标，
   假设世界坐标为(u，v，1)，图像坐标为(x，y)

   .. cpp:function:: void SimpleRadialCameraModel::WorldToImage(const T* params, const T u, const T v, T* x, T* y)

   .. code-block:: cpp

        template void SimpleRadialCameraModel::WorldToImage(const T* params, const T u, const T v, T* x, T* y) {

            const T f = params[0];

            const T c1 = params[1];

            const T c2 = params[2];

           // 对u，v进行畸变

            T du, dv;

            Distortion(&params[3], u, v, &du, &dv);

            *x = u + du;

            *y = v + dv;

           // 变换到图像坐标

            *x = f * *x + c1;

            *y = f * *y + c2; }

2. 将图像坐标转换为标准化的摄影机坐标。
   产生世界坐标为(u，v，1)。图像坐标为(x，y)

   .. cpp:function:: void SimpleRadialCameraModel::ImageToWorld(const T* params, const T x, const T y, T* u, T* v)

   .. code-block:: cpp

        template void SimpleRadialCameraModel::ImageToWorld(const T* params, const T x, const T y, T* u, T* v) {

        const T f = params[0];

        const T c1 = params[1];

        const T c2 = params[2];

        // 点到归一化平面

        *u = (x - c1) / f;

        *v = (y - c2) / f;

        IterativeUndistortion(&params[3], u, v); }

3. 得到畸变后的坐标

   .. math::

           \begin{cases}
           du = u(1+ k_1r^2 + k_2 r^4 + k_3r^6)\\
           dv = v(1+ k_1r^2 + k_2 r^4 + k_3r^6)
           \end{cases}~~~~~~~r^2 = x^2 + y^2

   x, y 在这里分别代表矫正后图像中(u, v)点像素分别在行向和列向与主点的距离。

   由于SimpleRadialCameraModel模型只有一个k，所以取到第二项即可，同时将x和y用u，v替换。

   **请注意：该公式左侧为校正前的坐标(du，dv)，右侧(u，v)是未发生畸变的校正后坐标。**

   .. cpp:function:: void SimpleRadialCameraModel::Distortion(const T* extra_params, const T u, const T v, T* du, T* dv)

   .. code-block:: cpp

        template void SimpleRadialCameraModel::Distortion(const T* extra_params, const T u, const T v, T* du, T* dv) {

        const T k = extra_params[0];

        const T u2 = u * u;

        const T v2 = v * v;

        const T r2 = u2 + v2;

        const T radial = k * r2;

        *du = u * radial;

        *dv = v * radial; }

4. 牛顿迭代法去除畸变

    .. cpp:function:: void BaseCameraModel::IterativeUndistortion(const T* params, T* u, T*v)

    .. code-block:: cpp

        template <typename CameraModel>
        template <typename T>

        void BaseCameraModel::IterativeUndistortion(const T* params, T* u, T*v) {

        // 使用具有中心差的数值微分进行牛顿迭代的参数，即使对于具有更高阶项的复杂相机模型，也要进行100次迭代就足够了。
        const size_t kNumIterations = 100;

        const double kMaxStepNorm = 1e-10;

        const double kRelStepSize = 1e-6;

        Eigen::Matrix2d J;

        const Eigen::Vector2d x0(*u, *v);

        Eigen::Vector2d x(*u, *v);

        Eigen::Vector2d dx;

        Eigen::Vector2d dx_0b;

        Eigen::Vector2d dx_0f;

        Eigen::Vector2d dx_1b;

        Eigen::Vector2d dx_1f;

        //std::numeric\_limits::epsilon()返回1与大于1的double类型最小值之间的差。
        for (size_t i = 0; i < kNumIterations; ++i) {

        const double step0 = std::max(std::numeric_limits<double>::epsilon(),
                                  std::abs(kRelStepSize * x(0)));

        const double step1 = std::max(std::numeric_limits<double>::epsilon(),
                                  std::abs(kRelStepSize * x(1)));

        CameraModel::Distortion(params, x(0), x(1), &dx(0), &dx(1));
        CameraModel::Distortion(params, x(0) - step0, x(1), &dx_0b(0), &dx_0b(1));
        CameraModel::Distortion(params, x(0) + step0, x(1), &dx_0f(0), &dx_0f(1));
        CameraModel::Distortion(params, x(0), x(1) - step1, &dx_1b(0), &dx_1b(1));
        CameraModel::Distortion(params, x(0), x(1) + step1, &dx_1f(0), &dx_1f(1));

        J(0, 0) = 1 + (dx_0f(0) - dx_0b(0)) / (2 * step0);
        J(0, 1) = (dx_1f(0) - dx_1b(0)) / (2 * step1);
        J(1, 0) = (dx_0f(1) - dx_0b(1)) / (2 * step0);
        J(1, 1) = 1 + (dx_1f(1) - dx_1b(1)) / (2 * step1);

        const Eigen::Vector2d step_x = J.inverse() * (x + dx - x0);
        x -= step_x;
        if (step_x.squaredNorm() < kMaxStepNorm)
            break;
        }

        *u = x(0);
        *v = x(1);

Camera
~~~~~~~~~

包含内参的相机类。
可以在多个图像之间共享相机，例如，如果同一“物理”相机使用完全相同的镜头和内在特性(焦距等)拍摄了多张照片。

相关函数
^^^^^^^^

1. 相机模型信息

.. cpp:function:: inline int Camera::ModelId() const;

.. cpp:function:: std::string Camera::ModelName() const;

.. cpp:function:: void Camera::SetModelId(const int model_id);

.. cpp:function:: void Camera::SetModelIdFromName(const std::string& model_name);

2. 相机长宽

.. cpp:function:: inline size_t Camera::Width() const;

.. cpp:function:: inline size_t Camera::Height() const;

.. cpp:function:: inline void Camera::SetWidth(const size_t width);

.. cpp:function:: inline void Camera::SetHeight(const size_t height);

3. 焦距信息

.. cpp:function:: double Camera::MeanFocalLength() const;

.. cpp:function:: double Camera::FocalLength() const;

.. cpp:function:: double Camera::FocalLengthX() const;

.. cpp:function:: double Camera::FocalLengthY() const;

.. cpp:function:: void Camera::SetFocalLength(const double focal_length);

.. cpp:function:: void Camera::SetFocalLengthX(const double focal_length_x);

.. cpp:function:: void Camera::SetFocalLengthY(const double focal_length_y);


4. 主点信息

.. cpp:function:: double Camera::PrincipalPointX() const;

.. cpp:function:: double Camera::PrincipalPointY() const;

.. cpp:function:: void Camera::SetPrincipalPointX(const double ppx);

.. cpp:function:: void Camera::SetPrincipalPointY(const double ppy);

5. 内参矩阵

.. cpp:function:: Eigen::Matrix3d Camera::CalibrationMatrix() const;

6. 获取参数向量中参数组的索引

.. cpp:function:: const std::vector& Camera::FocalLengthIdxs() const;

.. cpp:function:: const std::vector<size_t>& Camera::PrincipalPointIdxs() const;

.. cpp:function:: const std::vector<size_t>& Camera::ExtraParamsIdxs() const;

7. 改变尺寸进而改变焦距

.. cpp:function:: void Camera::Rescale(const double scale)

.. cpp:function:: void Camera::Rescale(const size_t width, const size_t height);

//-- 根据尺寸变换焦距 --//

.. code-block:: cpp

    void Camera::Rescale(const double scale) {

        CHECK_GT(scale, 0.0);

        const double scale_x =
            std::round(scale * width_) / static_cast<double>(width_);

        const double scale_y =
            std::round(scale * height_) / static_cast<double>(height_);

        width_ = static_cast<size_t>(std::round(scale * width_));

        height_ = static_cast<size_t>(std::round(scale * height_));

        SetPrincipalPointX(scale_x * PrincipalPointX());

        SetPrincipalPointY(scale_y * PrincipalPointY());

        if (FocalLengthIdxs().size() == 1) {
            SetFocalLength((scale_x + scale_y) / 2.0 * FocalLength());}

        else if (FocalLengthIdxs().size() == 2) {
            SetFocalLengthX(scale_x * FocalLengthX());
            SetFocalLengthY(scale_y * FocalLengthY());}

        else LOG(FATAL) << "Camera model must either have 1 or 2 focal length parameters.";
    }

//-- 根据长宽变换焦距 --//

.. code-block:: cpp

    void Camera::Rescale(const size_t width, const size_t height) {
        const double scale_x =
            static_cast<double>(width) / static_cast<double>(width_);

        const double scale_y =
            static_cast<double>(height) / static_cast<double>(height_);

        width_ = width;

        height_ = height;

        SetPrincipalPointX(scale_x * PrincipalPointX());

        SetPrincipalPointY(scale_y * PrincipalPointY());

        if (FocalLengthIdxs().size() == 1) {
            SetFocalLength((scale_x + scale_y) / 2.0 * FocalLength());}

        else if (FocalLengthIdxs().size() == 2) {
            SetFocalLengthX(scale_x * FocalLengthX());
            SetFocalLengthY(scale_y * FocalLengthY());}

        else LOG(FATAL) << "Camera model must either have 1 or 2 focal length parameters.";

    }

CameraRig
~~~~~~~~~~~~

包含有关摄影机装置的相对配置的信息。

相机装置由多个相机组成，这些相机在多个快照上具有严格的相对外部配置。

快照定义为装置中所有摄像机同时捕获的图像的集合。

相关函数
^^^^^^^^

1. 相机和快照的数量

.. cpp:function:: size_t CameraRig::NumCameras() const;

.. cpp:function:: size_t CameraRig::NumSnapshots() const;

2. 添加新的相机

将新相机添加到装置。
相对位姿可以包含虚拟值，然后可以使用ComputeRelativePoses方法从给定的重构中自动计算出相对位姿。

.. cpp:function:: void CameraRig::AddCamera(const camera_t camera_id, const Eigen::Vector4d& rel_qvec, const Eigen::Vector3d& rel_tvec);

3. 添加新的快照

将单个快照的图像添加到装置。快照由装置的所有摄像机捕获的图像组成。快照的所有图像共享相同的全局相机装置位姿。

.. cpp:function:: void CameraRig::AddSnapshot(const std::vector<image_t>& image_ids);

4. 获取装置中摄像机的相对姿势

.. cpp:function:: Eigen::Vector4d& CameraRig::RelativeQvec(const camera_t camera_id);

.. cpp:function:: const Eigen::Vector4d& CameraRig::RelativeQvec(const camera_t camera_id) const;

.. cpp:function:: Eigen::Vector3d& CameraRig::RelativeTvec(const camera_t camera_id);

.. cpp:function:: const Eigen::Vector3d& CameraRig::RelativeTvec(const camera_t camera_id) const;

5. 计算scale

通过求投影中心之间的平均距离，可以计算出从重建到摄像机装置尺寸的比例因子。

假设设备中至少有一对摄像机的基线为非零，否则该函数返回NaN。

.. cpp:function:: double CameraRig::ComputeScale(const Reconstruction& reconstruction) const;

6. 计算相对位姿

通过求所有快照上的相对位姿的平均值，可以从重建中计算相机装置中的相对姿态。

参考摄像机的姿势将是Identity。 这假定摄影机装置有在重建中配准的快照。

.. cpp:function:: void CameraRig::ComputeRelativePoses(const Reconstruction& reconstruction);

7. 计算装备的绝对相机姿态

装置的绝对摄影机位姿计算为装置中所有相对摄影机位姿及其在重建中对应图像位姿的平均值。

.. cpp:function:: void CameraRig::ComputeAbsolutePose(const size_t snapshot_idx, const Reconstruction& reconstruction, Eigen::Vector4d* abs_qvec, Eigen::Vector3d* abs_tvec) const;
