TranslationTransform
====================

计算两个点对之间的距离变换。

成员变量
-----------

   .. cpp:type:: Eigen::Matrix<double, kDim, 1> TranslationTransformEstimator::X_t;

   .. cpp:type:: Eigen::Matrix<double, kDim, 1> TranslationTransformEstimator::Y_t;

   .. cpp:type:: Eigen::Matrix<double, kDim, 1> TranslationTransformEstimator::M_t;

   .. cpp:member:: static const int TranslationTransformEstimator::kMinNumSamples = 1;


成员函数
------------

Estimate
~~~~~~~~~~

   计算点对的平均点之间的距离作为点对之间的位移变换。

   .. code-block:: cpp

      template <int kDim>
      std::vector<typename TranslationTransformEstimator<kDim>::M_t>
      TranslationTransformEstimator<kDim>::Estimate(const std::vector<X_t>& points1,
                                                    const std::vector<Y_t>& points2) {
         CHECK_EQ(points1.size(), points2.size());

         X_t mean_src = X_t::Zero();
         Y_t mean_dst = Y_t::Zero();

         for (size_t i = 0; i < points1.size(); ++i) {
            mean_src += points1[i];
            mean_dst += points2[i];
         }

         mean_src /= points1.size();
         mean_dst /= points2.size();

         std::vector<M_t> models(1);
         models[0] = mean_dst - mean_src;

         return models;
      }


Residuals
~~~~~~~~~~

   .. code-block:: cpp

      template <int kDim>
      void TranslationTransformEstimator<kDim>::Residuals(
            const std::vector<X_t>& points1, const std::vector<Y_t>& points2,
            const M_t& translation, std::vector<double>* residuals) {
         CHECK_EQ(points1.size(), points2.size());

         residuals->resize(points1.size());

         for (size_t i = 0; i < points1.size(); ++i) {
            const M_t diff = points2[i] - points1[i] - translation;
            (*residuals)[i] = diff.squaredNorm();
         }
      }