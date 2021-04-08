Least-Squares Fitting of Two 3-D Point Sets
=================================================

|:point_right:| \ `原文链接 <https://www.math.pku.edu.cn/teachers/yaoy/Fall2011/arun.pdf>`_

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
   &=& \sum\limits_{i=1}^N Trace(q_i'^TRq_i)\\
   &=& \sum\limits_{i=1}^N Trace(Rq_iq_i'^T)\\
   &=& Trace (\sum\limits_{i=1}^N Rq_iq_i'^T)\\
   &=& Trace (R \sum\limits_{i=1}^N q_iq_i'^T)\\
   &=& Trace(RH)
   \end{eqnarray}

定义：

.. math::

   H \triangleq \sum\limits_{i=1}^N q_iq_i'^T

.. note::

   :性质:

      (1) :math:`Trace(AB) = Trace(BA)`

      (2) :math:`Trace(A+B) = Trace(A) + Trace(B)`

.. important::

   :引理:

      对于任何正定矩阵 :math:`AA^T` 和任何正交矩阵 :math:`B` ，有

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

从而问题转换为：求一个  :math:`X`  ，使  :math:`XH`  可以表示为  :math:`AA^T`  的形式

对 :math:`H` 矩阵进行SVD奇异值分解：

.. math::

   H = U \Sigma V^T

令：

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

REFLECTION
--------------
Reflection称为反射变换（镜面反射），在数学上反射是把一个物体变换成它的镜像的映射。要反射一个平面图形，需要“镜子”是一条直线（反射轴），对于三维空间中的反射就要使用平面作为镜子。

反射变换同样是一个 **正交矩阵** ，显而易见它满足如下性质：

*  镜面反射是正交变换。

*  镜面反射的逆变换为镜面反射。

*  任意一个正交变换都可以表示成若干个镜面反射的乘积。

旋转变换和反射变换具有如下特性：

*  旋转矩阵和反射矩阵都是正交矩阵

*  旋转矩阵的行列式值为 +1，反射矩阵的行列值为 -1

*  旋转矩阵  :math:`R(\theta)`  的逆矩阵为 :math:`R(-\theta)`，反射矩阵的逆矩阵为其本身。也可以记为：旋转矩阵 :math:`RR^T = I`，反射矩阵 :math:`R'R'=I`

最简单的反射变换是沿某个轴/面的镜像，例如相对于 :math:`Z = 0` 平面的镜像变换为：  :math:`\left[\begin{matrix}1 & 0 & 0\\0 & 1 & 0\\0 & 0 & -1\end{matrix}\right]`

根据性质，一定可以把任意一个镜面变换拆成一个关于  :math:`Z = 0`  的镜面变换与一个旋转变换。也就是变成：

.. math::

   R' = \left[\begin{matrix}1 & 0 & 0\\0 & 1 & 0\\0 & 0 & -1\end{matrix}\right] R

之前使用SVD求解的 :math:`X` 一定是一个正交矩阵，但是并不是所有的正交矩阵都是旋转矩阵，也可能是一个反射矩阵（或者说包含了反射变换的矩阵）。因此我们还需要对所求得的 :math:`X` 进行行列式判断：

*  :math:`det(X) = 1`  ，则所求的 :math:`X` 是所求的旋转矩阵。

*  :math:`det(X) = -1` ，则所求的 :math:`X` 包含了镜像。

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

      有无限多的旋转和镜像对称的解使 :math:`\Sigma^2 = 0`

对于共面的情况， :math:`H` 的秩为2，即：

.. math::

   H = U \Sigma V^T = U \left[\begin{matrix}\sigma_1 & 0 & 0\\0 & \sigma_2 & 0\\0 & 0 & 0\end{matrix}\right]

由于 SVD 分解特征值是从大到小排序，则一定有：

.. math::

   H = \sigma_1 u_1v_1^T + \sigma_2 u_2 v_2^T + \sigma_3· u_3v_3^T = \sigma_1 u_1v_1^T + \sigma_2 u_2 v_2^T + 0 · u_3v_3^T

.. math::

   \sigma_1 > \sigma_2 > \sigma_3 = 0

如果存在一个解  :math:`X = VU^T = [v_1,v_2,v_3]U^T` 满足以上 :math:`H` 取得极大值，则一定有镜像变换：

.. math::

   R' = V'U^T = [v_1,v_2,-v_3]^T = [v_1,v_2,v_3] \left[\begin{matrix}1 & 0 & 0\\0 & 1 & 0\\0 & 0 & -1\end{matrix}\right]U^T

满足上式 :math:`H` 取得极大值。

所以当 :math:`det(VU^T) = -1` 时，想要求得的 :math:`R` 只需要去除中间乘的反射变换矩阵 :math:`\left[\begin{matrix}1 & 0 & 0\\0 & 1 & 0\\0 & 0 & -1\end{matrix}\right]`

也即：

.. math::

   R = VU^T = V'\left[\begin{matrix}1 & 0 & 0\\0 & 1 & 0\\0 & 0 & -1\end{matrix}\right]U^T

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

      *  :math:`H` 的一个奇异值（例如 :math:`\sigma_3` ）为零，那么

         .. math::

            \hat{R} = X' = V'U^T

         其中 :math:`V'` 是 :math:`V` 的第三列的符号取反得到的。

      *  :math:`H` 的奇异值没有0，则最小二乘解无法求解，需要使用类似RANSAC的技术。