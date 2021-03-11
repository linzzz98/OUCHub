.. default-domain:: cpp

CostFunctions
=============

BundleAdjustmentCostFunction
----------------------------

标准的BA 代价函数，用于可变的摄像机姿态，校准和点的参数。

.. code-block:: cpp

    template <typename CameraModel>
    class BundleAdjustmentCostFunction {
     public:
      explicit BundleAdjustmentCostFunction(const Eigen::Vector2d& point2D)
          : observed_x_(point2D(0)), observed_y_(point2D(1)) {}

      static ceres::CostFunction* Create(const Eigen::Vector2d& point2D) {
        //  优化量:
        //  2 表示 observed_x_ 和  observed_y_ 两个变量
        //  4，3，3，CameraModel::kNumParams 分别表示 const T* const qvec, const T* const tvec, const T* const point3D, const T* const camera_params的维度
        return (new ceres::AutoDiffCostFunction<
                BundleAdjustmentCostFunction<CameraModel>, 2, 4, 3, 3,
                CameraModel::kNumParams>(
            new BundleAdjustmentCostFunction(point2D)));
      }

      template <typename T>
      bool operator()(const T* const qvec, const T* const tvec,
                      const T* const point3D, const T* const camera_params,
                      T* residuals) const {
        // 旋转和平移
        T projection[3];
        ceres::UnitQuaternionRotatePoint(qvec, point3D, projection);
        projection[0] += tvec[0];
        projection[1] += tvec[1];
        projection[2] += tvec[2];

        // 投影到图像平面
        projection[0] /= projection[2];
        projection[1] /= projection[2];

        // 畸变并转换为像素空间
        CameraModel::WorldToImage(camera_params, projection[0], projection[1],
                                  &residuals[0], &residuals[1]);

        // 重投影误差
        residuals[0] -= T(observed_x_);
        residuals[1] -= T(observed_y_);

        return true;
      }

     private:
      const double observed_x_;
      const double observed_y_;
    };

其中， ceres::UnitQuaternionRotatePoint(qvec, point3D,
projection)的作用是：根据四元数q（单位范数\ :math:`|q|^2 = 1`\ ）旋转pt，如果\ :math:`|q|^2 = 2`\ ，则结果不是两倍。

.. cpp:function:: template<typename T> void UnitQuaternionRotatePoint(constTq[4], constTpt[3], Tresult[3])

BundleAdjustmentConstantPoseCostFunction
----------------------------------------

BA 代价函数，用于可变的摄像机校准和点的参数以及固定的摄像机位姿。

.. code-block:: cpp

    template <typename CameraModel>
    class BundleAdjustmentConstantPoseCostFunction {
     public:
      BundleAdjustmentConstantPoseCostFunction(const Eigen::Vector4d& qvec,
                                               const Eigen::Vector3d& tvec,
                                               const Eigen::Vector2d& point2D)
          : qw_(qvec(0)),
            qx_(qvec(1)),
            qy_(qvec(2)),
            qz_(qvec(3)),
            tx_(tvec(0)),
            ty_(tvec(1)),
            tz_(tvec(2)),
            observed_x_(point2D(0)),
            observed_y_(point2D(1)) {}

      static ceres::CostFunction* Create(const Eigen::Vector4d& qvec,
                                         const Eigen::Vector3d& tvec,
                                         const Eigen::Vector2d& point2D) {
        return (new ceres::AutoDiffCostFunction<
                BundleAdjustmentConstantPoseCostFunction<CameraModel>, 2, 3,
                CameraModel::kNumParams>(
            new BundleAdjustmentConstantPoseCostFunction(qvec, tvec, point2D)));
      }

      template <typename T>
      bool operator()(const T* const point3D, const T* const camera_params,
                      T* residuals) const {
        const T qvec[4] = {T(qw_), T(qx_), T(qy_), T(qz_)};

        // 旋转和平移
        T projection[3];
        ceres::UnitQuaternionRotatePoint(qvec, point3D, projection);
        projection[0] += T(tx_);
        projection[1] += T(ty_);
        projection[2] += T(tz_);

        // 投影到图像平面
        projection[0] /= projection[2];
        projection[1] /= projection[2];

        // 畸变并转换为像素空间
        CameraModel::WorldToImage(camera_params, projection[0], projection[1],
                                  &residuals[0], &residuals[1]);

        // 重投影误差
        residuals[0] -= T(observed_x_);
        residuals[1] -= T(observed_y_);

        return true;
      }

     private:
      const double qw_;
      const double qx_;
      const double qy_;
      const double qz_;
      const double tx_;
      const double ty_;
      const double tz_;
      const double observed_x_;
      const double observed_y_;
    };

RigBundleAdjustmentCostFunction
-------------------------------

Rig BA代价函数可用于可变的摄像机位姿，校准和点的参数。

与标准BA调整功能不同，此代价函数适用于在Rig内具有一致的摄像机相对位姿的摄影机。

代价函数首先将点投影到摄影机Rig的本地系统中，然后投影到Rig中的摄影机的本地系统中。

.. code-block:: cpp

    template <typename CameraModel>
    class RigBundleAdjustmentCostFunction {
     public:
      explicit RigBundleAdjustmentCostFunction(const Eigen::Vector2d& point2D)
          : observed_x_(point2D(0)), observed_y_(point2D(1)) {}

      static ceres::CostFunction* Create(const Eigen::Vector2d& point2D) {
        return (new ceres::AutoDiffCostFunction<
                RigBundleAdjustmentCostFunction<CameraModel>, 2, 4, 3, 4, 3, 3,
                CameraModel::kNumParams>(
            new RigBundleAdjustmentCostFunction(point2D)));
      }

      template <typename T>
      bool operator()(const T* const rig_qvec, const T* const rig_tvec,
                      const T* const rel_qvec, const T* const rel_tvec,
                      const T* const point3D, const T* const camera_params,
                      T* residuals) const {
        // Concatenate rotations.
        T qvec[4];

        // qvec = rel_qvec * rig_qvec
        ceres::QuaternionProduct(rel_qvec, rig_qvec, qvec);

        // Concatenate translations.
        T tvec[3];

        // tvec = R(rel_qvec) * rig_tvec
        ceres::UnitQuaternionRotatePoint(rel_qvec, rig_tvec, tvec);
        tvec[0] += rel_tvec[0];
        tvec[1] += rel_tvec[1];
        tvec[2] += rel_tvec[2];

        // Rotate and translate.
        T projection[3];

        // projection = R(qvec) * point3D
        ceres::UnitQuaternionRotatePoint(qvec, point3D, projection);
        projection[0] += tvec[0];
        projection[1] += tvec[1];
        projection[2] += tvec[2];

        // 投影到图像平面
        projection[0] /= projection[2];
        projection[1] /= projection[2];

        // 畸变并转换为像素空间
        CameraModel::WorldToImage(camera_params, projection[0], projection[1],
                                  &residuals[0], &residuals[1]);

        // 重投影误差
        residuals[0] -= T(observed_x_);
        residuals[1] -= T(observed_y_);

        return true;
      }

     private:
      const double observed_x_;
      const double observed_y_;
    };


RelativePoseCostFunction
------------------------

基于Sampson误差细化两视图几何的代价函数。

假定第一个位姿位于没有旋转的原点。
假定第二个姿势在第一个位姿周围的单位球面上，也就是说，第二个摄像机的姿势是通过3D旋转和具有单位范数的3D平移来参数化的。

.. code-block:: cpp

    class RelativePoseCostFunction {
    public:
      RelativePoseCostFunction(const Eigen::Vector2d& x1, const Eigen::Vector2d& x2)
          : x1_(x1(0)), y1_(x1(1)), x2_(x2(0)), y2_(x2(1)) {}

      static ceres::CostFunction* Create(const Eigen::Vector2d& x1,
                                         const Eigen::Vector2d& x2) {
        return (new ceres::AutoDiffCostFunction<RelativePoseCostFunction, 1, 4, 3>(
            new RelativePoseCostFunction(x1, x2)));
      }

      template <typename T>
      bool operator()(const T* const qvec, const T* const tvec,
                      T* residuals) const {
        Eigen::Matrix<T, 3, 3, Eigen::RowMajor> R;
        ceres::QuaternionToRotation(qvec, R.data());

        // 叉积t x R的矩阵表示
        Eigen::Matrix<T, 3, 3> t_x;
        t_x << T(0), -tvec[2], tvec[1], tvec[2], T(0), -tvec[0], -tvec[1], tvec[0],
            T(0);

        // 本质矩阵
        const Eigen::Matrix<T, 3, 3> E = t_x * R;

        // 归一化的图像坐标
        const Eigen::Matrix<T, 3, 1> x1_h(T(x1_), T(y1_), T(1));
        const Eigen::Matrix<T, 3, 1> x2_h(T(x2_), T(y2_), T(1));

        // 桑普森误差的平方
        const Eigen::Matrix<T, 3, 1> Ex1 = E * x1_h;
        const Eigen::Matrix<T, 3, 1> Etx2 = E.transpose() * x2_h;
        const T x2tEx1 = x2_h.transpose() * Ex1;
        residuals[0] = x2tEx1 * x2tEx1 /
                       (Ex1(0) * Ex1(0) + Ex1(1) * Ex1(1) + Etx2(0) * Etx2(0) +
                        Etx2(1) * Etx2(1));

        return true;
      }

     private:
      const double x1_;
      const double y1_;
      const double x2_;
      const double y2_;
    };

Sampson Distance的平方为：

.. math::


   || \epsilon||^2 = \frac{(x_2^TFx_1)^2}{(Fx_1)_1^2 + (Fx_1)_2^2 + (F^Tx_2)_1^2 + (F^Tx_2)_2^2}


