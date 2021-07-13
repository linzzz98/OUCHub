Motion Averaging
==================

小孔模型

.. math::

   \left[
   \begin{matrix}
   u\\v\\1
   \end{matrix}
   \right] = \left[
   \begin{matrix}
   I~|~0
   \end{matrix}
   \right] \underbrace{
   \left[
   \begin{matrix}
   R & T\\0 & 1
   \end{matrix}
   \right]}_{M} \left[
   \begin{matrix}
   X\\Y\\Z\\1
   \end{matrix}
   \right]

3D 配准

.. math::

   \left[
   \begin{matrix}
   X'\\Y'\\Z'\\1
   \end{matrix}
   \right] = \underbrace{
   \left[
   \begin{matrix}
   R & T\\0 & 1
   \end{matrix}
   \right]}_{M} \left[
   \begin{matrix}
   X\\Y\\Z\\1
   \end{matrix}
   \right]

.. note::

   将平均问题表示为：

   *  :math:`M \in \mathbb{SE}(3)` （刚体 3d 欧几里得运动）

   *  :math:`R \in \mathbb{SO}(3)` （刚体 3d 旋转）

   *  :math:`T \in \mathbb{R}^3` （刚体 3d 位移）

   *  :math:`t \in S^2 ` （旋转的方向 :math:`t = \frac{T}{||T||}` ）


.. attention::

   先旋转再平移和先平移在旋转是不同的。

   :先旋转后平移:

   .. math::
      \begin{eqnarray}
      P' &=& RP + T\\
      &\Downarrow&\\
      P_i &=& R_iP_0 + T_i\\
      P_j &=& R_jP_0 + T_j\\
      &\Downarrow&\\
      R_{ij} &=& R_jR_i^{-1}\\
      T_{ij} &=& T_j - R_jR_i^{-1}T_i
      \end{eqnarray}

   :先平移后旋转:

   .. math::
      \begin{eqnarray}
      P' &=& R(P + T)\\
      &\Downarrow&\\
      P_i &=& R_i(P_0 + T_i)\\
      P_j &=& R_j(P_0 + T_j)\\
      &\Downarrow&\\
      R_{ij} &=& R_jR_i^{-1}\\
      T_{ij} &=& T_j - T_i
      \end{eqnarray}

   以上的结果相同，但是在表示形式上不同。

视图图
-----------

.. figure:: 1.jpg
   :figclass: algin-center

* Viewgraph（视图图 ） 表示为 :math:`\mathcal{G = \{V, E\}}`

   * 顶点表示相机

   * 边表示相机和相机之间的相对运动

* N个图片序列描述了N - 1个运动

* 一般将某一个相机作为原点

* 相机序列可以提供最多 :math:`^N C_2 = \frac{N(N-1)}{2}` 对相对运动

* 相对运动形成高度冗余的方程组

假设知道顶点的值 :math:`v_i` ，那么边值（ :math:`v_{ij}` ）很容易根据顶点值来估计。

.. math::

   v_{ij} = v_j - v_i

.. important::

   运动平均问题是上述问题的逆问题，即给定边值 :math:`\{v_{ij} \in \mathcal{E}\}` ，估计顶点的值 :math:`v_i \in \mathcal{V}`

观察到的相对位移：

:math:`v_j - v_i = v_{ij}` ，循环 :math:`v_j - v_{ij} - v_i = 0`

.. note::

   当存在约束的时候， :math:`v_j - v_i \ne v_{ij}` ，不同的路径会产生不同的结果，观测值也不再连续（"consistent"），因此问题的解就变为找到与边最一致的估计。

.. figure:: 2.jpg
   :figclass: align-center

等式的线性系统为： :math:`AV = V_{ij}`

其中 :math:`A` 编码了视图图，是图的关联矩阵。

与图拉普拉斯相关的 :math:`L = A^TA` ，图的拉普拉斯在表征问题难度方面发挥作用。

.. note::

   拉普拉斯矩阵是用于三维以下的图形的计算，可以表示复杂的几何结构。

   假设 :math:`In(G)` 为一幅图的关系矩阵， :math:`In(G)` 的尺寸为 :math:`E \times V` ，其中 :math:`V` 为图中节点， :math:`E` 为图中的边，如 :math:`i` 点为 :math:`j` 边的起点，则 :math:`In(G)(i,j) = -1` ，终点则为 :math:`In(G)(i,j) = 1` ,其他情况均为 :math:`0` .

   则拉普拉斯矩阵为：

   .. math::

      L(G) = In(G)^TIn(G)

   拉普拉斯矩阵是对称的，秩为 :math:`V - 1` ，一个特征值为0，是半正定的，每行每列加起来为0。

规范自由度（Gauge freedom） :math:`AV = A(V+s1)`

.. figure:: 3.jpg
   :figclass: align-center

考虑运动矩阵 :math:`M`

*  :math:`M_j M_i^{-1} = M_{ij}, \forall i \ne j`

*  类似的有 :math:`v_j - v_i = v_{ij}`

*  :math:`=` 左侧为 要估计的全局运动， :math:`=` 右侧的是观测值。

.. figure:: 4.jpg
   :figclass: align-center

:math:`M_ij = M_jM_i^{-1}, \forall i \ne j \Rightarrow M_{ij} M_i - M_j = 0`

全局运动 :math:`M_g = \{M_1,···,M_N\}`

等式系统 :math:`BM_g = 0`

这里的运动群是李群。