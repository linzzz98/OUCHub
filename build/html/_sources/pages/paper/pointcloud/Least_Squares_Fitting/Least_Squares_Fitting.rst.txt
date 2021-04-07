Least-Squares Fitting of Two 3-D Point Sets
=================================================

|:point_right:| \ `原文链接 <https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=4767965>`_

INTRODUCTION
--------------

给定两组3D点云集合 :math:`\{p_i\}` 和 :math:`\{p_i'\}` （ :math:`3 \times 1` ），从而有

.. math::

   p_i' = Rp_i + T + N_i

目标是求一个 :math:`R,T` 去最小化：

.. math::

   \Sigma^2 = \sum\limits_{i=1}^N ||p_i' - (Rp_i + T)||^2


DECOUPLING TRANSLATION AND ROTATION
----------------------------------------

定义质心：

.. math::

   p  \triangleq \frac{1}{N} \sum\limits_{i=1}^N p_i \\

   p' \triangleq \frac{1}{N} \sum\limits_{i=1}^N p_i' \\

对 :math:`\Sigma^2` 函数进行变形：

.. math::

   \begin{eqnarray}
   \Sigma^2 &=& \sum\limits_{i=1}^N ||p_i' - (Rp_i + T)||^2\\
   &=& \sum\limits_{i=1}^N || p_i' - Rp_i -T + p' - p' + Rp - Rp||\\
   &=& \sum\limits_{i=1}^N || (p_i' - p' - R(p_i - p)) + (p' - (Rp + T))||^2\\
   &=& \sum\limits_{i=1}^N (|| p_i' - p' - R(p_i - p)  || ^2 + || p' - (Rp + T) || ^2 \\
   &~&~~~ +2(p_i' - p' - R(p_i - p))(p' - (Rp + T)))
   \end{eqnarray}

令：

.. math::

   q_i \triangleq p_i - p\\\\

   q_i' \triangleq p_i' - p'

因为：

.. math::

   \sum\limits_{i=1}^N (p_i' - p' - R(p_i - p))(p' - (Rp + T)) = 0


因此问题转换为：

.. math::

   \Sigma^2 =  \sum\limits_{i=1}^N ||q_i' - Rq_i||^2 + n||p' - (Rp + T)||^2

因为左右两边都 :math:`\ge 0`，且左边只与 :math:`R` 相关，因此可以先求出 :math:`R` 再利用 :math:`R` 求出第二项。

.. note::

   经过变形，最小二乘问题变换成两个子问题：

   1. 找到 :math:`\hat{R}` 去最小化 :math:`\Sigma^2`

   2. 通过 :math:`\hat{T} = p' - \hat{R} p` 计算位移


AN SVD ALGORITHM FOR FINDING  :math:`\hat{R}`
-------------------------------------------------------

将 :math:`\Sigma^2` 的右边展开：

.. math::

   \begin{eqnarray}
   \Sigma^2 &=& \sum\limits_{i=1}^N (q_i' - Rq_i)^T(q_i' - Rq_i)\\
   &=& \sum\limits_{i=1}^N (q_i'^Tq_i' + q_i^TR^TRq_i - q_i'^TRq_i - q_i^TR^Tq_i')\\
   &=& \sum\limits_{i=1}^N (q_i'^Tq_i' + q_i^Tq_i - 2q_i'^TRq_i)
   \end{eqnarray}

.. note::

   :向量的内积:

      .. math::

         \alpha = (a_1,a_2,...,a_n)^T, \beta = (b_1,b_2,...,b_n)^T\\

      .. math::

         \Downarrow

      .. math::

         \beta^T\alpha = \alpha^T\beta = a_1b_1 + a_2b_2 +...+a_nb_n （向量内积）

   因为  :math:`q_i^TR^T` 为 :math:`1\times 3 * 3\times 3 = 1 \times 3` ，且 :math:`q_i'` 为 :math:`3 \times 1` ，从而：

   .. math::

      q_i^TR^T q_i' = q_i'^T Rq_i

   所以：

   .. math::

      q_i'^TRq_i + q_i^TR^Tq_i' = 2q_i'^TRq_i


因此，最小化 :math:`\Sigma^2` 问题转换为最大化

.. math::

   \begin{eqnarray}
   F &=& \sum\limits_{i=1}^N q_i'^TRq_i \\
   &=& Trace(\sum\limits_{i=1}^N Rq_iq_i'^T) = Trace(RH)
   \end{eqnarray}

定义：

.. math::

   H \triangleq \sum\limits_{i=1}^N q_iq_i'^T

.. note::

   :二次型的迹的性质:

      设 :math:`x` 是一个 :math:`n \times 1` 的列向量，二次型为 :math:`x'Ax` ，二次型是一个 :math:`1\times 1`  的矩阵，其迹为自身：

      .. math::

         x'Ax = Trace(x'Ax) = Trace(Axx') = tr(xx'A)

   根据这个性质，由于 :math:`q_i'^TRq_i` 为 :math:`1 \times 1` 的“伪二次型”，且 :math:`q_i,q_i'` 均为  :math:`3 \times 1` 维，因此有：

   .. math::

      \sum\limits_{i=1}^N q_i'^TRq_i = Trace(\sum\limits_{i=1}^N Rq_iq_i'^T)

.. important::

   :引理:

      对于任何正定矩阵 :math:`AA'` 和任何正交矩阵 :math:`B` ，有

      .. math::

         Trace(AA^T) \ge Trace(BAA^T)

   .. note::

      :证明:

         令 :math:`a_i` 为矩阵 :math:`A` 的第 :math:`i` 列，从而

         .. math::

            Trace(BAA^T) = Trace(A^TBA) = \sum\limits_{i} a_i^T(Ba_i)

         根据柯西-施瓦茨不等式，对于欧式空间中任意向量 :math:`\alpha, \beta` 有：

         .. math::

            (\alpha, \beta)^2 \le (\alpha,\alpha)(\beta,\beta)

         其中定义 :math:`(\alpha, \beta)` 是向量 :math:`\alpha, \beta` 的内积，当且仅当 :math:`\alpha, \beta` 线性相关时，:math:`"="`  成立

         从而：

         .. math::

            a_i^T(Ba_i) \le \sqrt{(a_i^Ta_i)(a_i^TB^TBa_i)} = a_i^Ta_i

         所以：

         .. math::

            Trace(BAA^T) \le \sum\limits_i a_i^Ta_i = Trace(AA^T)

对 :math:`H` 矩阵进行SVD奇异值分解：

.. math::

   H = U \Sigma V^T

可以得到：

.. math::

   X = VU^T

从而：

.. math::

   \begin{eqnarray}
   XH &=& VU^TU\Sigma V^T\\
   &=& V\Sigma V^T
   \end{eqnarray}

这是对称且正定的。 因此，根据引理，对于任何 :math:`3\times 3` 的正交矩阵 :math:`B` ，

.. math::

   Trace(XH) \ge Trace(BXH)

因此，在所有 :math:`3 \times 3` 的正交矩阵中， :math:`X` 使 :math:`F` 最大化。 如果 :math:`det(X) = +1` ，则 :math:`X` 是所求的旋转。

但是，如果 :math:`det(X) = -1` ，则 :math:`X` 是 ``reflection（镜像对称）``

NOISELESS CASE
---------------

假设没有噪声（ :math:`N_i = 0` ），很显然有一个解 :math:`\hat{R}` （ :math:`det(\hat{R}) = 1` ）。

因为 :math:`\Sigma^2 = 0`，所以 :math:`\{q_i'\}` 和 :math:`\{\hat{R} q_i\}` 是全等的。

从几何方面考虑，很容易看出对于 :math:`\{q_i\}` 上的点有三种情况：

.. note::

   :不共面:

      解有唯一的旋转，没有镜像对称解使 :math:`\Sigma^2 = 0`

   :共面但不共线:

      解有一个唯一的旋转以及一个唯一的镜像对称使 :math:`\Sigma^2 = 0`

   :共线:

      解有无限多的旋转和镜像对称使 :math:`\Sigma^2 = 0`

回到共面的情况下，可以很容易的证明，当且仅当 :math:`H` 的三个奇异值之一为0时，点 :math:`\{q_i\}` 是共面的。 令三个奇异值分别为 :math:`\lambda_1 > \lambda_2 > \lambda_3 = 0` ，从而

.. math::

   H = \lambda_1 u_1v_1^T + \lambda_2 u_2 v_2^T + 0· u_3v_3^T

这里的 :math:`u_i` 和 :math:`v_i` 是 :math:`U,V` 的列向量。

.. caution::

   更改 :math:`u_3` 或 :math:`v_3` 的符号不会更改 :math:`H` 的值。

   因此，如果 :math:`X = VU^T` 最小化 :math:`\Sigma^2` ，那么 :math:`X' = V'U^T` 也会最小化 :math:`\Sigma^2` 。

   这里 :math:`V' = [v_1,v_2,-v_3]`

.. important::

   如果 :math:`X` 镜像对称，则 :math:`X'` 是旋转，反之亦然。

   因此，如果SVD算法给出的解 :math:`X` 为 :math:`det(X) = -1` ，则 :math:`X'= V'U^T` 即为所需的旋转。

.. note::

   顺带一提，当且仅当 :math:`H` 的三个奇异值中的两个相等时， :math:`\{q_i\}` 是共线的。


SUMMARY OF ALGORITHM
----------------------------

:step 1: 从点云 :math:`\{p_i\}, \{p_i'\}` 中计算质心 :math:`p,p'` ，然后得到去质心点云 :math:`\{q_i\}, \{q_i'\}`

:step 2: 计算 :math:`3\times 3` 的矩阵：

   .. math::

      H \triangleq \sum\limits_{i=1}^N q_i q_i'^T

:step 3: 通过SVD分解 :math:`H`

   .. math::

      H = U \Sigma V^T

:step 4: 计算 :math:`X`

   .. math::

      X = VU^T

:step 5: 计算 :math:`X` 的行列式 :math:`det(X)`

   * 如果 :math:`det(X) = +1` ，那么 :math:`\hat{R} = X`

   * 如果 :math:`det(X) = -1`

      *  :math:`H` 的一个奇异值（例如 :math:`\lambda_3` ）为零，那么

         .. math::

            \hat{R} = X' = V'U^T

         其中 :math:`V'` 是 :math:`V` 的第三列的符号取反得到的。

      *  :math:`H` 的奇异值没有0，则最小二乘解无法求解，需要使用类似RANSAC的技术。