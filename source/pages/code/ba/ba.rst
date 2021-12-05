Bundle Adjustment
=================

INCLUDING
---------

:ceres:

   .. code-block:: cpp

      #include "ceres/ceres.h"
      #include "ceres/rotation.h"
      #include "ceres/loss_function.h"
      #include "ceres/covariance.h"

ENUM
----

.. code-block:: cpp

   enum BACameraType {
      // 透视相机
      BA_PERSPECTIVE_CAMERA,
      // 鱼眼相机
      BA_FISHEYE_CAMERA,
   };

.. code-block:: cpp

   enum {
      // 焦距
      BA_CAMERA_FOCAL,
      // Focal-X
      BA_CAMERA_K1,
      // Focal-Y
      BA_CAMERA_K2,
      // 相机参数个数
      BA_CAMERA_NUM_PARAMS
   };


.. code-block:: cpp

   enum {
      // 旋转向量X-Y-Z
      BA_SHOT_RX,
      BA_SHOT_RY,
      BA_SHOT_RZ,
      // 位移向量X-Y-Z
      BA_SHOT_TX,
      BA_SHOT_TY,
      BA_SHOT_TZ,
      // 个数
      BA_SHOT_NUM_PARAMS
   };

STRUCT
------

相机
~~~~~

.. code-block:: cpp

   struct BACamera {
      // 相机ID
      std::string id;
      // 是否固定
      bool constant;
      // 相机类型
      virtual BACameraType type() = 0;
   };

透视相机
~~~~~~~~~

.. code-block:: cpp

   struct BAPerspectiveCamera : public BACamera{
      double parameters[BA_CAMERA_NUM_PARAMS];
      double focal_prior;
      double k1_prior;
      double k2_prior;

      BACameraType type() { return BA_PERSPECTIVE_CAMERA; }
      double GetFocal() { return parameters[BA_CAMERA_FOCAL]; }
      double GetK1() { return parameters[BA_CAMERA_K1]; }
      double GetK2() { return parameters[BA_CAMERA_K2]; }
      void SetFocal(double v) { parameters[BA_CAMERA_FOCAL] = v; }
      void SetK1(double v) { parameters[BA_CAMERA_K1] = v; }
      void SetK2(double v) { parameters[BA_CAMERA_K2] = v; }
   };

鱼眼相机
~~~~~~~~~

.. code-block:: cpp

   struct BAFisheyeCamera : public BACamera{
      double parameters[BA_CAMERA_NUM_PARAMS];
      double focal_prior;
      double k1_prior;
      double k2_prior;

      BACameraType type() { return BA_FISHEYE_CAMERA; }
      double GetFocal() { return parameters[BA_CAMERA_FOCAL]; }
      double GetK1() { return parameters[BA_CAMERA_K1]; }
      double GetK2() { return parameters[BA_CAMERA_K2]; }
      void SetFocal(double v) { parameters[BA_CAMERA_FOCAL] = v; }
      void SetK1(double v) { parameters[BA_CAMERA_K1] = v; }
      void SetK2(double v) { parameters[BA_CAMERA_K2] = v; }
   };

位姿信息
~~~~~~~~~~

.. code-block:: cpp

   struct BAShot {
     double parameters[BA_SHOT_NUM_PARAMS];
     double covariance[BA_SHOT_NUM_PARAMS * BA_SHOT_NUM_PARAMS];
     bool constant;
     int exif_orientation;
     std::string camera;
     std::string id;

     double GetRX() { return parameters[BA_SHOT_RX]; }
     double GetRY() { return parameters[BA_SHOT_RY]; }
     double GetRZ() { return parameters[BA_SHOT_RZ]; }
     double GetTX() { return parameters[BA_SHOT_TX]; }
     double GetTY() { return parameters[BA_SHOT_TY]; }
     double GetTZ() { return parameters[BA_SHOT_TZ]; }
     void SetRX(double v) { parameters[BA_SHOT_RX] = v; }
     void SetRY(double v) { parameters[BA_SHOT_RY] = v; }
     void SetRZ(double v) { parameters[BA_SHOT_RZ] = v; }
     void SetTX(double v) { parameters[BA_SHOT_TX] = v; }
     void SetTY(double v) { parameters[BA_SHOT_TY] = v; }
     void SetTZ(double v) { parameters[BA_SHOT_TZ] = v; }
     double GetCovariance(int i, int j) { return covariance[i * BA_SHOT_NUM_PARAMS + j]; }
   };

点信息
~~~~~~~~

.. code-block:: cpp

   struct BAPoint {
     double coordinates[3];
     bool constant;
     double reprojection_error;
     std::string id;

     double GetX() { return coordinates[0]; }
     double GetY() { return coordinates[1]; }
     double GetZ() { return coordinates[2]; }
     void SetX(double v) { coordinates[0] = v; }
     void SetY(double v) { coordinates[1] = v; }
     void SetZ(double v) { coordinates[2] = v; }
   };

观测
~~~~~~~~

.. code-block:: cpp

   struct BAObservation {
     double coordinates[2];
     BACamera *camera;
     BAShot *shot;
     BAPoint *point;
     bool on_tag;
     bool optimize;
   };

Tag
~~~~~~~~

.. code-block:: cpp

   struct BATag {
     double p1[3]; //top left
     double p2[3]; //top right
     double p3[3]; //bottom right
     double p4[3]; //bottom left
     double size; //meters
   };

Error
~~~~~~

:旋转误差:

   .. code-block:: cpp

      struct BARotationPrior {
        BAShot *shot;
        double rotation[3];
        double std_deviation;
      };

:位移误差:

   .. code-block:: cpp

      struct BATranslationPrior {
        BAShot *shot;
        double translation[3];
        double std_deviation;
      };

:位置误差:

   .. code-block:: cpp

      struct BAPositionPrior {
        BAShot *shot;
        double position[3];
        double std_deviation;
      };

:点位置先验信息:

   .. code-block:: cpp

      struct BAPointPositionPrior {
        BAPoint *point;
        double position[3];
        double std_deviation;
      };

:地面控制点观测值:

   .. code-block:: cpp

      struct BAGroundControlPointObservation {
        BACamera *camera;
        BAShot *shot;
        double coordinates3d[3];
        double coordinates2d[2];
      };

LOSS FUNCTION
---------------

.. cpp:member:: ceres::LossFunction *loss;
.. cpp:member:: double loss_function_threshold_;

* TruncatedLoss

   .. code-block:: cpp

      loss = new TruncatedLoss(loss_function_threshold_);

   .. code-block:: cpp

      class TruncatedLoss : public ceres::LossFunction {
         public:
            explicit TruncatedLoss(double t)
               : t2_(t*t) {
               CHECK_GT(t, 0.0);
            }

            virtual void Evaluate(double s, double rho[3]) const {
               if (s >= t2_) {
                  // Outlier.
                  rho[0] = t2_;
                  rho[1] = std::numeric_limits<double>::min();
                  rho[2] = 0.0;
            } else {
               // Inlier.
               rho[0] = s;
               rho[1] = 1.0;
               rho[2] = 0.0;
            }
         }

         private:
            const double t2_;
      };

* TrivialLoss

   .. math::

      \rho(s) = s

   .. code-block:: cpp

      loss = new ceres::TrivialLoss();

* HuberLoss

   .. math::

      \rho(s) =
      \begin{cases}
      s~~~s<1\\
      2 \sqrt{s-1}~~ s> 1
      \end{cases}

   .. code-block:: cpp

      loss = new ceres::HuberLoss(loss_function_threshold_);

* SoftLOneLoss

   .. math::

      \rho(s) = 2(\sqrt{1 + s} - 1)

   .. code-block:: cpp

      loss = new ceres::SoftLOneLoss(loss_function_threshold_);

* CauchyLoss

   .. math::

      \rho(s) = log(1 + s)

   .. code-block:: cpp

      loss = new ceres::CauchyLoss(loss_function_threshold_);

* ArctanLoss

   .. math::

      \rho(s) = arctan(s)

   .. code-block:: cpp

      loss = new ceres::ArctanLoss(loss_function_threshold_);

FUNCTION
---------

世界坐标系 :math:`\longrightarrow` 相机坐标系
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. math::

   P_c = R_{w \rightarrow c} P_w + T_{w \rightarrow c}

.. code-block:: cpp

   template <typename T>
   void WorldToCameraCoordinates(const T* const shot,
                                 const T world_point[3],
                                 T camera_point[3]) {
     ceres::AngleAxisRotatePoint(shot + BA_SHOT_RX, world_point, camera_point);
     camera_point[0] += shot[BA_SHOT_TX];
     camera_point[1] += shot[BA_SHOT_TY];
     camera_point[2] += shot[BA_SHOT_TZ];
   }

----------

透视相机投影
~~~~~~~~~~~~~~~

:归一化:

   .. math::

      x_p = x / z\\
      y_p = y / z

:计算畸变:

   .. math::
      r^2 = x_p^2 + y_p^2\\

   .. math::
      distortion = 1 + r^2 * (k_1 + k_2 * r^2)

:投影:

   .. math::

      projection_x = f * distortion * x_p\\
      projection_y = f * distortion * y_p

.. code-block:: cpp

   template <typename T>
   void PerspectiveProject(const T* const camera,
                           const T point[3],
                           T projection[2]) {
     T xp = point[0] / point[2];
     T yp = point[1] / point[2];

     // Apply second and fourth order radial distortion.
     const T& l1 = camera[BA_CAMERA_K1];
     const T& l2 = camera[BA_CAMERA_K2];
     T r2 = xp * xp + yp * yp;
     T distortion = T(1.0) + r2  * (l1 + r2 * l2);

     // Compute final projected point position.
     const T& focal = camera[BA_CAMERA_FOCAL];
     projection[0] = focal * distortion * xp;
     projection[1] = focal * distortion * yp;
   }

----------

鱼眼相机投影
~~~~~~~~~~~~~~~

.. code-block:: cpp

   template <typename T>
   void FisheyeProject(const T* const camera,
                       const T point[3],
                       T projection[2]) {
     const T& focal = camera[BA_CAMERA_FOCAL];
     const T& k1 = camera[BA_CAMERA_K1];
     const T& k2 = camera[BA_CAMERA_K2];
     const T &x = point[0];
     const T &y = point[1];
     const T &z = point[2];

     T l = sqrt(x * x + y * y);
     T theta = atan2(l, z);
     T theta2 = theta * theta;
     T theta_d = theta * (T(1.0) + theta2 * (k1 + theta2 * k2));
     T s = focal * theta_d / l;

     projection[0] = s * x;
     projection[1] = s * y;
   }

COST FUNCTION
-------------

透视相机投影
~~~~~~~~~~~~~~~~~

.. code-block:: cpp

   struct PerspectiveReprojectionError {
     PerspectiveReprojectionError(double observed_x, double observed_y, double std_deviation)
         : observed_x_(observed_x)
         , observed_y_(observed_y)
         , scale_(1.0 / std_deviation)
     {}

     template <typename T>
     bool operator()(const T* const camera,
                     const T* const shot,
                     const T* const point,
                     T* residuals) const {
       T camera_point[3];
       WorldToCameraCoordinates(shot, point, camera_point);

       if (camera_point[2] <= T(0.0)) {
         residuals[0] = residuals[1] = T(99.0);
         return true;
       }

       T predicted[2];
       PerspectiveProject(camera, camera_point, predicted);

       // The error is the difference between the predicted and observed position.
       residuals[0] = T(scale_) * (predicted[0] - T(observed_x_));
       residuals[1] = T(scale_) * (predicted[1] - T(observed_y_));

       return true;
     }

     double observed_x_;
     double observed_y_;
     double scale_;
   };

------------------------

鱼眼相机投影
~~~~~~~~~~~~~~~~~

.. code-block:: cpp

   struct FisheyeReprojectionError {
      FisheyeReprojectionError(double observed_x, double observed_y, double std_deviation)
         : observed_x_(observed_x)
         , observed_y_(observed_y)
         , scale_(1.0 / std_deviation)
      {}

      template <typename T>
      bool operator()(const T* const camera,
                     const T* const shot,
                     const T* const point,
                     T* residuals) const {
         T camera_point[3];
         WorldToCameraCoordinates(shot, point, camera_point);

         if (camera_point[2] <= T(0.0)) {
            residuals[0] = residuals[1] = T(99.0);
            return true;
         }

         T predicted[2];
         FisheyeProject(camera, camera_point, predicted);

         // The error is the difference between the predicted and observed position.
         residuals[0] = T(scale_) * (predicted[0] - T(observed_x_));
         residuals[1] = T(scale_) * (predicted[1] - T(observed_y_));

         return true;
      }

      double observed_x_;
      double observed_y_;
      double scale_;
   };

GCP投影
~~~~~~~~~~~

.. code-block:: cpp

   struct GCPPerspectiveProjectionError {
      GCPPerspectiveProjectionError(
         double world[3], double observed[2], double std_deviation)
            : world_(world)
            , observed_(observed)
            , scale_(1.0 / std_deviation)
      {}

      template <typename T>
      bool operator()(const T* const camera,
                     const T* const shot,
                     T* residuals) const {
         T world_point[3] = { T(world_[0]), T(world_[1]), T(world_[2]) };
         T camera_point[3];
         WorldToCameraCoordinates(shot, world_point, camera_point);

         if (camera_point[2] <= T(0.0)) {
            residuals[0] = residuals[1] = T(99.0);
            return true;
         }

         T predicted[2];
         PerspectiveProject(camera, camera_point, predicted);

         // The error is the difference between the predicted and observed position.
         residuals[0] = T(scale_) * (predicted[0] - T(observed_[0]));
         residuals[1] = T(scale_) * (predicted[1] - T(observed_[1]));

         return true;
      }

      double *world_;
      double *observed_;
      double scale_;
   };

TAG
---------

尺度误差
~~~~~~~~~~~~

.. math::

   \sum\limits_{i=1}^T (||V_{12}^i||_2 - S)^2 + (||V_{23}^i||_2 - S)^2 + (||V_{34}^i||_2 - S)^2 + (||V_{41}^i||_2 - S)^2

.. code-block:: cpp

   struct TagSizeError
   {
      TagSizeError(double tag_size, double std_deviation) : tag_size_(tag_size), scale_(1.0 / std_deviation)
      {}

      template <typename T>
      bool operator()(const T* const tagpoint1, const T* const tagpoint2, T* residuals) const
      {
         // length of v12
         T vx = tagpoint1[0] - tagpoint2[0];
         T vy = tagpoint1[1] - tagpoint2[1];
         T vz = tagpoint1[2] - tagpoint2[2];
         T v12 = sqrt(vx*vx + vy*vy + vz*vz);

         // residual
         residuals[0] = T(scale_) * (v12 - tag_size_);

         return true;
      }

      double tag_size_;
      double scale_;
   };

正交误差
~~~~~~~~~~~~~~~~~~

.. math::

   \sum\limits_{i=1}^T (V_{12}^i · V_{23}^i)^2 + (V_{23}^i · V_{34}^i)^2 + (V_{34}^i · V_{41}^i)^2 + (V_{41}^i · V_{12}^i)^2

.. code-block:: cpp

   struct TagOrthogonalityError
   {
     TagOrthogonalityError(double std_deviation) : scale_(1.0 / std_deviation)
     {}

     template <typename T>
     bool operator()(const T* const tagpoint1, const T* const tagpoint2, const T* const tagpoint3, T* residuals) const
     {
       // v12
       T v12x = tagpoint1[0] - tagpoint2[0];
       T v12y = tagpoint1[1] - tagpoint2[1];
       T v12z = tagpoint1[2] - tagpoint2[2];
       T len_v12 = sqrt( (v12x*v12x) + (v12y*v12y) + (v12z*v12z) );
       v12x = v12x / len_v12;
       v12y = v12y / len_v12;
       v12z = v12z / len_v12;

       // v32
       T v32x = tagpoint3[0] - tagpoint2[0];
       T v32y = tagpoint3[1] - tagpoint2[1];
       T v32z = tagpoint3[2] - tagpoint2[2];
       T len_v32 = sqrt( (v32x*v32x) + (v32y*v32y) + (v32z*v32z) );
       v32x = v32x / len_v32;
       v32y = v32y / len_v32;
       v32z = v32z / len_v32;

       // v12 . v23
       residuals[0] = (v12x * v32x) + (v12y * v32y) + (v12z * v32z);

       return true;
     }

     double scale_;
   };
