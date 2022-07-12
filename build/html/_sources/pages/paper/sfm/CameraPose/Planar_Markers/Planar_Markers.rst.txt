Mapping and Localization from Planar Markers
============================================

本文提出了一种新方法，可以同时解决一组方形平面标记的映射和定位问题。

1. 创建成对相对标记位姿的颤动，从中获得初始姿势图。

2. 姿态图可能包含小的成对位姿误差，当传播时，会导致大误差。因此，沿着图的Cycle basis（循环基底） distribute旋转和平移误差，以获得校正的位姿图。

3. 通过最小化所有观察帧中平面标记的重投影误差来执行全局位姿优化。

.. note::

   循环基底（它是循环的最小集合）

   .. figure:: 1.jpg
      :figclass: align-center

SfM和Slam关于相机定位大都依赖于关键点法，然而关键点匹配对在尺度、旋转的不变性上相当有限，在很多情况下无法识别不同视点下的场景。

方形平面标记被设计为易于从更广泛的位置检测，方形标记使用外部（易于检测）黑色边框和内部二进制代码进行识别、错误检测和纠正。
单个标记提供四个对应点，可以以亚像素精度进行定位，以获得准确的相机位姿估计。

本文提出了解决平面标记映射和定位问题的方法。

:贡献:

   1. 将标记映射问题作为稀疏束调整问题的变体来解决，但考虑到标记的四个角必须联合优化。该方法减少了要优化的变量数量，并确保在优化期间强制执行角之间的真实距离。

   2. 提出了一种基于图的方法来获得处理歧义问题的标记初始图。 为此，首先创建 **a quiver of poses**，从中获得初始姿势图，然后对其进行优化，沿其循环分布旋转和平移误差。

考虑任意参考系 :math:`a` 中的三维点  :math:`p_a = (x,y,z)` 。

为了将这样的点表达到另一个参考系统 b 中，它必须经过旋转和平移。

.. math::

   \zeta = (r,t)|r,t \in R^3

使用罗德里格斯的旋转公式，可以从旋转向量 :math:`r` 获得旋转矩阵 :math:`R` 为：

.. math::

   R = I_{3\times 3} + \overline{r} sin\theta + \overline{r}^2 (1-cos\theta)

其中 :math:`I_{3\times 3}` 是单位矩阵， :math:`\overline{r}` 表示反对称矩阵。

然后，结合 t，得到 :math:`4 \times 4` 矩阵：

.. math::

   \gamma = \Gamma(\zeta) = \left[
   \begin{matrix}
   R & t^T\\0 & 1
   \end{matrix}
   \right]

可用于将点从 :math:`a` 转换为 :math:`b` 为：

.. math::

   \left[
   \begin{matrix}
   p_b^T\\1
   \end{matrix}
   \right] = \gamma \left[
   \begin{matrix}
   p_a^T\\1
   \end{matrix}
   \right]

为了简化符号，将定义运算符 :math:`(·)` 来表示： :math:`p_b = \gamma · p_a`

点 :math:`p` 在相机平面中投影到像素 :math:`u \in R^2` 中。 假设相机参数是已知的，投影可以作为一个函数获得：

.. math::

   u = \Psi(\delta, \gamma,p)

其中：

.. math::

   \delta = (f_x, f_y, c_x, c_y, k_1, ..., k_n)

为相机内参，由焦距 :math:`(f_x,f_y)` 、光心 :math:`(c_x, c_y)` 和畸变参数 :math:`(k_1,...,k_n)` 组成。

.. note::

   符号说明：

   *  :math:`f^t:` 相机在 t 时刻获取的图像。

   *  frs：帧参考系统。 获取帧时参考系统以相机原点为中心。 每个帧都有自己的frs。

   *  mrs：marker参考系统。 以marker为中心的参考系统。 每个标记都有自己的mrs。

   *  grs：全局参考系。希望获得所有度量的公共参考系统。

   *  :math:`\gamma_i: mrs \rightarrow grs`  将点从 :math:`marker_i` 的参考系转换为全局参考系。

   *  :math:`\gamma_{j,i}: mrs \rightarrow mrs` 将点从 :math:`marker_i` 的参考系转换为 :math:`marker_j` 的参考系。

   *  :math:`\gamma^t: grs \rightarrow frs` 将点从全局参考系转换为第 :math:`t` 帧的参考系。

   *  :math:`\gamma^t_i: mrs \rightarrow frs` 将点从 :math:`marker_i` 的参考系转换到第 :math:`t` 帧的参考系。

   *  :math:`\gamma^t_{j,i}: mrs \rightarrow mrs` 根据在第 :math:`t` 帧中两者的observation，将点从 :math:`marker_i` 的参考系转换为 :math:`marker_j` 的参考系。

   一般来说，当使用变换 :math:`\gamma` 时，上标指的是帧，而下标指的是marker。

本文将问题表述为在一组帧中找到的标记角点的重投影误差的最小化，获得一个非线性方程。由于 LM 算法是一种局部搜索方法，因此需要良好的初始估计以避免陷入局部最小值。

虽然问题类似于BA，但公式通过联合优化每个标记的四个角点来减少变量的数量。 它还确保在优化期间强制执行marker之间的实际距离。

考虑一个正方形平面marker，边长为 s，其四个角可以相对于marker中心表示为：

.. math::

   c_1 = (s / 2, -s / 2, 0)\\
   c_2 = (s / 2, s / 2, 0)\\
   c_3 = (-s / 2, s / 2, 0)\\
   c_4 = (-s / 2, s / 2, 0)

用 :math:`M = \{m\}` 表示放置在环境中的一组marker， 并用 :math:`\gamma_m` 表示它们的姿势，即从 mrs 移动点到 grs 的变换。

.. important::

   请注意，出于映射目的，仅考虑观察至少两个标记的帧，即  :math:`|ft| > 1`。


.. attention::

   在本文的问题中，位姿 :math:`\gamma_m` 和 :math:`\gamma^t` 是要优化的参数，而 :math:`\omega_i^t` 是可用的观测值。

   如果需要，相机参数 :math:`\delta` 也可以作为优化过程的一部分。

   然后，该问题类似于BA问题。 但主要区别在于，虽然 BA 假设点彼此独立，但在本文提出的公式中，marker的四个点形成了一个仅由六个参数（即 :math:`\gamma_m` ）表示的刚性对象。

   :优点:

      1. 减少参数数量，降低优化的复杂性。

      2. 确保marker连续角点（lt - rt - rb - lb）之间的距离为 :math:`s` ，使用一般 BA 公式无法保证这一点。

   在任何情况下，问题都会减少到最小化所有帧中标记角点的平方重投影误差，从而找到参数的值。

   在帧 :math:`f^t` 中检测到的 :math:`marker_i`  的重投影误差是通过比较其角点的观察投影而获得的。

   .. math::

      u_{i,j}^t, j = 1...4, i\in f^t

   与预测的

   .. math::

      e_i^t = \sum\limits_j [\Psi(\delta, \gamma^t, \gamma_i · c_j) - u_{i,j}^t]^2

   其中 :math:`\Psi` 是定义的投影函数

   因此，整个帧中的总重投影误差表示为标记位姿、帧位姿和相机内参的函数：

   .. math::

      e(\gamma_1, ..., \gamma_M, \gamma^1, ... , \gamma^N, \delta) = \sum\limits_t \sum\limits_{i\in f^t} e_i^t

   其中 :math:`M` 和 :math:`N` 分别代表marker和帧的数量。


----

令 Q 为pose quiver，其中节点表示marker，边表示它们之间的相对位姿。 用

.. math::

   \epsilon^t = \{\gamma_i^t | i \in f^t\}

使用平面位姿估计方法为帧 :math:`f^t` 中检测到的标记估计的位姿集合。

元素 :math:`\gamma_i^t \in \epsilon^t :mrs → frs` ，表示将点从 :math:`marker_i` 的 mrs 移动到frs 的 :math:`f^t` 的变换。

.. note::

   平面位姿估计器返回两位姿，一个是正确的，另一个对应于模糊解。

   在大多数情况下，一个解的重投影误差远大于另一个解的重投影误差，因此不存在二义性问题，即很明显，重投影误差最小的解是好的解。

   在其他一些情况下，两种重投影误差非常相似。 很难判断哪种解决方案是好的，因此放弃对该 :math:`marker` 的观察，即没有为该特定标记添加到 :math:`\epsilon^t` 的解。

   因此 :math:`|\epsilon^t| \le |f^t|`

可以使用 :math:`\epsilon^t` 中的元素来获得观察到的 :math:`marker` 之间的相对位姿。

定义 :math:`\gamma^t(mrs\rightarrow mrs)` ，作为根据 :math:`f^t` 中的观测，将点从 :math:`marker_i` 的参考系转换到 :math:`marker_j` 的参考系的位姿，计算公式为：

.. math::

   \gamma_{j,i}^t = (r_j^t)^{-1} \gamma_i^t = \left[
   \begin{matrix}
   R_{j,i}^t & t_{j,i}^t\\0 & 1
   \end{matrix}
   \right]

然后将用 :math:`n = |ξt|` 表示：

.. math::

   \Psi^t = \{\gamma_{2,1}^t, \gamma_{3,1}^t, ···, \gamma_{n,1}^t, \gamma_{3,2}^t,···,\gamma_{n,n-1}^t\}

以表示此类变换的所有组合的集合，从 i 到 j 的变换及其逆可以很容易地计算为：

.. math::

   \gamma_{i,j}^t = (\gamma_{j,i}^t)^{-1}


Initial pose graph
---------------------

使用来自 quiver  :math:`Q` 的最佳 intermarker 位姿，创建有向位姿图 :math:`G` ，其中节点表示标记，边缘表示它们的相对位姿。

每条边  :math:`e = (i, j)`，定义权重:

.. math::

   \omega(e) = e_{j,i}(\hat{\gamma}_{j,i}),