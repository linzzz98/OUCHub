SimilarityTransform
========================

通过Eigen::umeyama函数来计算两组向量的旋转变换

``Umeyama`` 算法是为了计算两组数据之间的位置关系，比如说，现在有两组位于不同坐标系下的点位数据（可以是2D，也可是是3D），若事先已经知道点位之间的对应关系，则利用 ``Umeyama`` 算法可以计算出两组数据间的旋转与平移矩阵。

.. parsed-literal::

    \ `Least-Squares Estimation of Transformation Parameters Between Two Point Patterns <http://www.stanford.edu/class/cs273/refs/umeyama.pdf>`_

.. note::

   该算法的目标是计算一组 :math:`R,t` 使得目标函数最优：

   .. math::

      \frac{1}{n} \sum\limits_{i=1}^n||q_i - (cRp_i + t)||_2^2

   最终的判断标准是距离的平方和，也就是一个最小二乘估计问题。

   计算结果为：

   .. math::

      T = \left[
      \begin{matrix}
      cR & t \\ 0 & 1
      \end{matrix}
      \right]

   其中 :math:`c` 为缩放系数。

成员变量
-----------

   .. cpp:type:: Eigen::Matrix<double, kDim, 1> SimilarityTransformEstimator::X_t;

   .. cpp:type:: Eigen::Matrix<double, kDim, 1> SimilarityTransformEstimator::Y_t;

   .. cpp:type:: Eigen::Matrix<double, kDim, kDim + 1> SimilarityTransformEstimator::M_t;

   .. cpp:member:: static const int SimilarityTransformEstimator::kMinNumSamples = kDim;

成员函数
---------------

Estimate
~~~~~~~~~

   .. code-block:: cpp

      template <int kDim, bool kEstimateScale>
      std::vector<typename SimilarityTransformEstimator<kDim, kEstimateScale>::M_t>
      SimilarityTransformEstimator<kDim, kEstimateScale>::Estimate(
            const std::vector<X_t>& src, const std::vector<Y_t>& dst) {
         CHECK_EQ(src.size(), dst.size());

         Eigen::Matrix<double, kDim, Eigen::Dynamic> src_mat(kDim, src.size());
         Eigen::Matrix<double, kDim, Eigen::Dynamic> dst_mat(kDim, dst.size());
         for (size_t i = 0; i < src.size(); ++i) {
            src_mat.col(i) = src[i];
            dst_mat.col(i) = dst[i];
         }

         const auto model = Eigen::umeyama(src_mat, dst_mat, kEstimateScale)
                               .topLeftCorner(kDim, kDim + 1);

         if (model.array().isNaN().any()) {
            return std::vector<M_t>{};
         }

         return {model};
      }

Residuals
~~~~~~~~~~~

   .. code-block:: cpp

      template <int kDim, bool kEstimateScale>
      void SimilarityTransformEstimator<kDim, kEstimateScale>::Residuals(
            const std::vector<X_t>& src, const std::vector<Y_t>& dst, const M_t& matrix,
            std::vector<double>* residuals) {
         CHECK_EQ(src.size(), dst.size());

         residuals->resize(src.size());

         for (size_t i = 0; i < src.size(); ++i) {
            const Y_t dst_transformed = matrix * src[i].homogeneous();
            (*residuals)[i] = (dst[i] - dst_transformed).squaredNorm();
         }
      }

