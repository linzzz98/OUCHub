Iterative Reweighted Least Squares
==================================

对IRLS的具体介绍可以移步：:doc:`Iterative Reweighted Least Squares </pages/knowledge/Math/LeastSquares/IRLS/IRLS>`

为了说明这个算法，将把问题看作是寻找一组联立线性方程组的最优近似解：

.. math::

   \left[
   \begin{matrix}
   a_{11} & a_{12} & a_{13} & ··· & a_{1N}\\
   a_{21} & a_{22} & a_{23}\\
   a_{31} & a_{32} & a_{33}\\
   \vdots &  &  &  & \vdots\\
   a_{M1} &  &  & ··· & a_{MN}
   \end{matrix}
   \right] \left[
   \begin{matrix}
   x_1\\x_2\\x_3\\ \vdots \\x_N
   \end{matrix}
   \right]=
   \left[
   \begin{matrix}
   b_1\\b_2\\b_3\\ \vdots \\ b_M
   \end{matrix}
   \right]

或者，以矩阵表示法

.. math::

   Ax = b

.. note::

   上式给出了一个  :math:`M \times N` 实矩阵 :math:`A` 和一个 :math:`M \times 1` 向量 :math:`b` ，并且想要找到 :math:`N \times 1`
   向量 :math:`x` 。 只有当 :math:`A` 是非奇异的（平方和满秩）时，才有唯一的精确解。 否则，根据某种近似标准寻求近似解。

如果 :math:`b` 不在 :math:`A` 的范围空间（ :math:`A` 的列所跨越的空间），则没有精确的的解，因此，通过最小化由下式定义的方程误差向量的范数（或其他一些度量）来解决近似问题

.. math::

   e = Ax - b

Least Squared Error Approximation
---------------------------------

:math:`Ax = b` 的广义解（最佳近似解）通常被认为是使 :math:`e` 的某个范数或其他度量最小化的 :math:`x` 。

如果该问题没有唯一解，则施加进一步的条件，例如最小化 :math:`x` 的范数，并且该组合问题始终有唯一解。

:math:`l_2` 或均方根误差或欧几里得范数是 :math:`\sqrt{e^Te}` 并且其最小化具有解析解（Analytical solution）。

.. note::

   :解析解:
      解析解(Analytical solution) 就是根据严格的公式推导，给出任意的自变量就可以求出其因变量，也就是问题的解，然后可以利用这些公式计算相应的问题。所谓的解析解是一种包含分式、三角函数、指数、对数甚至无限级数等基本函数的解的形式。用来求得解析解的方法称为解析法(Analytical techniques)，解析法即是常见的微积分技巧，例如分离变量法等。解析解是一个封闭形式(Closed-form) 的函数，因此对任一自变量，我们皆可将其带入解析函数求得正确的因变量。因此，解析解也被称为封闭解(Closed-form solution)。

   :数值解:
      数值解(Numerical solution) 是采用某种计算方法，如有限元法， 数值逼近法，插值法等得到的解。别人只能利用数值计算的结果，而不能随意给出自变量并求出计算值。当无法藉由微积分技巧求得解析解时，这时便只能利用数值分析的方式来求得其数值解。在数值分析的过程中，首先会将原方程加以简化，以利于后来的数值分析。例如，会先将微分符号改为差分（微分的离散形式）符号等，然后再用传统的代数方法将原方程改写成另一种方便求解的形式。这时的求解步骤就是将一自变量带入，求得因变量的近似解，因此利用此方法所求得的因变量为一个个离散的数值，不像解析解为一连续的分布，而且因为经过上述简化的操作，其正确性也不如解析法可靠。

则这个平方误差定义为：

.. math::

   ||e||^2_2 = \sum\limits_i e^2_i = e^Te

如果 :math:`A` 具有完整的行或列秩，则最小化时会产生 :math:`Ax = b` 的精确或近似解。

* 如果 :math:`A` 有 :math:`M = N` ，（平方和非奇异），那么精确解是：

   .. math::

      x = A^{-1} b

*  如果 :math:`A` 有 :math:`M > N` ，（over specified）那么具有最小二乘方程误差的近似解是：

   .. math::

      A^TAx = A^Tb \rightarrow  x = [A^TA]^{-1}A^Tb

   .. note::

      证明：

      * 前置结论

         1.  :math:`tr(AB) = tr(BA)`

         2.  :math:`tr(ABC) = tr(BCA) = tr(CAB)`

         3.  :math:`\nabla_A tr(AB) = B^T`

         4.  :math:`tr(A) = tr(A^T)`

         5.  :math:`tr(a) = a`

         6.  :math:`\nabla_A tr(ABA^TC) = CAB+C^TAB^T`

         其中tr表示矩阵的迹，大写字母为矩阵，小写字母为实数， :math:`\nabla` 表示求导。

      * 公式推导

         作差

         .. math::

            Ax - b = [a_1^Tx - b_1 : a_m^T - b_m]

         构建最小二乘

         .. math::

            \frac{1}{2} (Ax-b)^T(Ax-b) = \frac{1}{2} \sum\limits_{i=1}^m (a_i^Tx - b_i)^2

         对 :math:`x` 求导

         .. math::

            \nabla_x \frac{1}{2} (Ax - b)^T(Ax - b) = \nabla_x tr(x^TA^TAx - x^TA^tb - b^TAx + b^Tb)

         利用结论（2）（4）（5）

         .. math::

            \nabla_x \frac{1}{2} (Ax-b)^T(Ax-b) = \nabla_x tr[xx^TA^TA - b^TAx - b^TAx]

         .. attention::

            * :math:`tr(\underbrace{x^T}_A \underbrace{A^TA}_B \underbrace{x}_C) = tr(\underbrace{x}_C \underbrace{x^T}_A \underbrace{A^TA}_B)`

            * :math:`tr(\underbrace{x^T A^T b}_A)` =  :math:`tr(\underbrace{b^T Ax}_{A^T})`

            * :math:`tr(b^Tb) = tr(a) = a \longrightarrow \nabla_x(a) = 0` （a为常数）

         利用结论（6）

         .. math::

            \nabla_x tr(xx^TA^TA) = \nabla_x tr(\underbrace{x}_A · \underbrace{I}_B · \underbrace{x^T}_{A^T} · \underbrace{A^TA}_C)

         从而

         .. math::

            \nabla_x (xx^TA^TA) = A^TA·x·I + (A^TA)^T · x · I^T = 2 · A^TAx

         利用结论（1）（3）

         .. math::

            \nabla_x tr(2 · \underbrace{b^TA}_B \underbrace{x}_A) = \nabla_x tr(2 · \underbrace{x}_A \underbrace{b^TA}_B) = 2 · A^Tb

         从而有：

         .. math::

            \frac{1}{2} (Ax-b)^T(Ax-b) = A^TAx - A^Tb = 0

         则有：

         .. math::

            A^TAx = A^Tb \longrightarrow x = (A^TA)^{-1}A^Tb


* 如果 :math:`A` 有 :math:`M < N` ，（under specified）那么具有最小范数的近似解是：

   .. math::

      Ax = AA^T(AA^T)^{-1}b \rightarrow x = A^T[AA^T]^{-1}b

.. note::

   这些公式假设 :math:`A` 具有完整的行或列秩，但如果不是，则使用伪逆求广义解。

Weighted Least Squared Error Approximation
------------------------------------------

使用加权的二范数来强调或不强调方程组中的某些分量：

.. math::

   ||We||^2_2 = \sum\limits_i w_i^2e_i^2 = e^T W^T W e

其中 :math:`W` 是一个对角矩阵，对角线元素是权重 :math:`w_i` ：

.. math::

   W = \left[
   \begin{matrix}
   w_1 &  & \\ & ··· & \\ &  & w_p
   \end{matrix}
   \right]_{p\times p}

* 如果 :math:`A` 有 :math:`M > N` ，（over specified），那么最小加权方程误差解是：

   .. math::

      x = [A^TW^TWA]^{-1}A^TW^TWb

   .. note::

      证明：

         构建最小二乘

         .. math::

            \frac{1}{2}(WAx - Wb)^T(WAx - Wb) = \frac{1}{2}\sum\limits_{i=1}^m(w_i^Ta_i^T x - b_i)^2

         对 :math:`x` 求导

         .. math::
            \begin{eqnarray}
            &&\nabla_x \frac{1}{2}(WAx - Wb)^T(WAx - Wb) \\&=&
            \nabla_x tr(x^TA^TW^TWAx - 2b^TW^TWAx + b^TW^TWb)
            \end{eqnarray}


         从而有

         .. math::
            \begin{eqnarray}
            \nabla_x tr(x^TA^TW^TWAx) &=& A^TW^TWA x + (A^TW^TWA)^T x \\&=& 2·(A^TW^TWA)x
            \end{eqnarray}

         和

         .. math::

            \nabla_x tr(2·b^TW^TWAx) = \nabla_x tr(2·xb^TW^TWA) = 2 · A^TW^TWb

         从而有

         .. math::

            \frac{1}{2}(WAx - Wb)^T(WAx - Wb) = (A^TW^TWA)x - A^TW^TWb = 0

         则有：

         .. math::

            (A^TW^TWA)x = W^TA^TWb \longrightarrow x = (A^TW^TWA)^{-1}A^TW^TWb


* 如果 :math:`A` 有 :math:`M < N` ，（under specified）那么最小加权范数解是：

   .. math::

      x = [W^TW]^{-1}A^T[A[W^TW]^{-1}A^T]^{-1}b

这些加权近似问题的解可以作为接下来开发的迭代重加权最小二乘 (IRLS) 算法的基础。

Approximation with Other Norms and Error Measures
--------------------------------------------------

大多数关于 :math:`Ax = b` 的近似解的讨论都是关于最小化 :math:`l2` 方程误差 :math:`||Ax = b||` 或解  :math:`||x||_2` 的 l2 范数的结果

更一般的情况下，即对于 :math:`p` 大于 1 时向量 :math:`x` 的 :math:`l_p` 范数的定义是：

.. math::

   ||e||_p = (\sum\limits_{i}|e_i|^p)^{\frac{1}{p}}

上式等价于优化：

.. math::

   ||e||_p^p = \sum\limits_i |e_i|^p

对于秩小于 :math:`M` 或 :math:`N` 的情况，可以使用一种范数来最小化方程误差范数，而使用另一种范数来最小化范数的解。

.. figure:: 1.jpg
   :figclass: align-center
   :scale: 75%

上图为 :math:`l_p` 范数的不同的 :math:`p` 取值（0.2，0.1，1，2，10）

:math:`p=0.2` 时对小值依然有较大的惩罚，使它们趋于零，（和1范数一样）可以实现解的稀疏性。因此在某些场景，比如去模糊过程中常使用1（0.2）范数作为解约束。

The lp Norm Approximation
--------------------------

IRLS（迭代重加权最小二乘法）算法允许从加权最小二乘法的解析解构建迭代算法，并通过迭代重加权收敛到最佳 :math:`l_p` 近似。

方程多于未知数的超定系统
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

如果在求解一组超定方程时提出 :math:`l_p` 近似问题，它来自定义方程误差向量

.. math::

   e = Ax - b

并最小化在 :math:`||e||_p = (\sum\limits_{i}|e_i|^p)^{\frac{1}{p}}` 或等价的 :math:`||e||_p^p = \sum\limits_i |e_i|^p` 中定义的 :math:`p` 范数，注意：这些都不能直接最小化。

然而，确实有公式来结束加权平方误差的最小值：

.. math::

   ||We||_2^2 = \sum\limits_n w_n^2 |e_n|^2

其中之一是：

.. math::

   x = [A^TW^TWA]^{-1}A^TW^TWb

其中 :math:`W` 是误差权重 :math:`w_i` 的对角矩阵。

迭代重加权最小二乘法 (IRLS)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. math::

   ||e||_p^p = \sum\limits_i |e_i|^p = \sum\limits_i |e_i|^{(p-2)}|e_i|^2 = \sum\limits_i w_n^2|e_i|^2 = ||We||_2^2

.. important::

   该算法的核心：等价于解加权最小平方误差近似问题，只是权值 :math:`W` 在迭代过程中不断变化。

   .. math::

      w_n = e(n)^{(p-2)}/2

   因为对角阵 :math:`W` 根据上次误差 :math:`e` 计算得到，因此会不断变化。

   该算法以 :math:`W = I` 的初始加权值开始， 用 :math:`x = [A^TW^TWA]^{-1}A^TW^TWb` 求解初始 :math:`x` 的值。然后用 :math:`e = Ax - b` 求解新误差，然后用于设置一个新的加权矩阵 :math:`W` ，其中对角元素为：

   .. math::

      w(n) = e(n)^{(p-2) / 2}

   在 :math:`x = [A^TW^TWA]^{-1}A^TW^TWb` 的下一次迭代中使用，并得到一个新的解 :math:`x` 并重复步骤直到收敛。

   伪代码为：

   .. figure:: 2.jpg
      :figclass: algin-center


如果在求解一组超定方程时提出 :math:`l_p` 近似问题，它来自将方程误差范数定义为：

.. math::

   ||e||_p = (\sum\limits_n |e(n)|^p)^{1/p}

并找到 :math:`x` 以最小化方程误差的 :math:`p` 范数。

这等效于解决适当权重的最小加权平方误差问题：

.. math::

   ||e||_p = (\sum\limits_n w(n)^2 |e(n)|^2 )^{1/2}

