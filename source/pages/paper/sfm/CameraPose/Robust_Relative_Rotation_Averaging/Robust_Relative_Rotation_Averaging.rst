Robust Relative Rotation Averaging
===================================

SfM 恢复三维点云和相机结构最流行的方法是BA的非线性优化方法，将3D结构和相机的生成模型与观察到的匹配图像点相匹配。BA的原理是最小化相机平面上的重投影误差。

但是作为非线性优化算法，BA需要良好的初始化，因为它只保证收敛到局部最小值，并且BA受异常值过多鲁棒性不足和无法收敛的问题所困扰。

使用两帧之间的对极几何，只能恢复第二个相机相对于第一个的航向方向（heading direction），而不是它们之间实际3D translation 的比例。 但是，可以使用它们的对极几何恢复相机对之间的3D相对旋转。

因此，一种常见的方法是首先单独解决3D旋转的运动平均问题，然后在3D平移的估计中利用该解决方案。一旦解决了相机的运动，使用多视图三角剖分找到3D结构点的位置就明显容易得多，这为BA求解提供了一个很好的初值。

本文以几个重要的方式概括和改进了《Efficient and Robust Large-Scale Rotation Averaging》中的解决方案：

Reduction to Iteratively Reweighted Least Squares
----------------------------------------------------

文章将最小化代价函数：

.. math::

   R_v = \mathop{argmin}_{\{R_1, R_2, ···, R_N\}} \sum\limits_{(i,j)\in \epsilon} \rho(d(R_{ij},R_jR_i^{-1}))

简化为迭代优化问题。 在每次迭代中，这个优化问题都使用拟牛顿法解决，从而得到一种对异常值既有效又鲁棒的整体平均方法。

上面的代价函数可以进一步写为：

.. math::

   \begin{eqnarray}
   R_v &=& \mathop{argmin}_{\{R_1, R_2, ···, R_N\}} \sum\limits_{(i,j)\in \epsilon} \rho(d(R_{ij},R_jR_i^{-1}))\\
       &=& \mathop{argmin}_{\{R_1, R_2, ···, R_N\}} \sum\limits_{(i,j)\in \epsilon} \rho(||\omega(R_j^{-1}R_{ij}R_i)||)\\
       &=& \mathop{argmin}_{\{R_1, R_2, ···, R_N\}} \sum\limits_{(i,j)\in \epsilon} \rho(||\omega(\Delta R_{ij})||)\\
   \end{eqnarray}

其中 :math:`\Delta R_{ij} = R_j^{-1} R_{ij} R_i` ，需要注意的是给定旋转 :math:`R_v` 的当前估计值，对于摄像机（ :math:`V` 中的顶点），:math:`||\Delta R_{ij}||`  表示 :math:`R_{ij}` 的摄像机  :math:`i`  和  :math:`j`  之间观察到的相对旋转 :math:`R_{ij}` 与当前用 :math:`R_jR_i^{-1}` 所估计相对旋转之间的差异

.. note::

   在李代数表示中选择canonical或欧几里得度量会对旋转群 SO(3) 上测地线距离进行直观定义。这个距离很容易通过熟悉的 3D 旋转轴角度参数化来指定。

   在轴角形式中， :math:`3 \times 1` 矢量 :math:`\omega` 表示角  :math:`||\omega||`  绕轴 :math:`\omega / ||\omega||` 旋转。

   旋转矩阵 :math:`R` 与其轴角 :math:`\omega` 之间的关系由下式给出：

   .. math::

      \begin{eqnarray}
         &&R &=& exp([\omega]_x)\\
         &&[\omega]_x &=& log(R)
      \end{eqnarray}

   其中 :math:`[\omega]_x` 是 :math:`\omega` 的反对称矩阵：

   .. math::

      [\omega]_x = \left[
      \begin{matrix}
      0 & -\omega_3 & \omega_2\\
      \omega_3 & 0 & -\omega_1\\
      -\omega_2 & \omega_1 & 0
      \end{matrix}
      \right]

   反对称矩阵 :math:`[\omega]_x` 定义了旋转群 SO(3) 的李代数。

   通常情况下：

   * :math:`R(\omega)`  表示通过应用于  :math:`[\omega]_x \in so(3)` 的指数映射获得的 3D 旋转；

   *  :math:`\omega(R)` 表示从 :math:`R \in SO(3)` 中提取的  :math:`\omega` 的 :math:`3 \times 1`  的向量。

   对于绕不同轴的两个 3D 旋转， :math:`R(\omega_1) R(\omega_2) \ne R(\omega_1 + \omega_2)`

   反而， :math:`R(\omega_1) R(\omega_2) = R(BCH(\omega_1, \omega_2))` ，其中 :math:`BCH(·,·)` 是Baker-Campbell-Hausdorff 形式，表示为两个李代数项 :math:`\omega_1` 和  :math:`\omega_2`  的级数。

   对于旋转群 SO(3)，BCH 级数有一个闭式表达式  :math:`BCH(\omega_1,\omega_2) = \alpha \omega_1 + \beta \omega_2 + \gamma \omega_1 \times \omega_2` ，其中标量  :math:`\alpha,\beta,\gamma`  是  :math:`\omega_1,\omega_2` 的函数。

   由于SO(3) 上的距离度量本质上是bi-invariant的，所以有：

   .. math::

      \begin{eqnarray}
      && d(R_1,R_2) = d(R_2,R_1) = d(I,R_2R_1^{-1})\\
      &=& \frac{1}{\sqrt{2}} ||log(R_2R_1^{-1})||_F = ||\omega(R_2R_1^{-1}||\\
      &=& ||BCH(\omega_2,-\omega_1)||
      \end{eqnarray}

   从而：:math:`d(R_{ij},R_jR_i^{-1}) = ||\omega(R_j^{-1}R_{ij}R_i)||`


下面考虑一种迭代方法来最小化的目标函数。

令当前对 :math:`R_v` 的估计为 :math:`\{R_1,···,R_N\}` ，在当前的迭代中、对 :math:`R_v` 进行更新来使损失函数的值下降。

令此次更新为 :math:`\{\Delta R_1, ···, \Delta R_N\}` ，则更新后的 :math:`R_v` 为 :math:`\{R_1\Delta R_1, ···, R_N\Delta R_N\}` 。

因此，在给定的迭代中，目标是最小化：

.. math::

   \sum\limits_{(i,j) \in \epsilon} \rho (||\omega(\Delta R_j^{-1} \Delta R_{ij} \Delta R_i)||)

对于每个单独的旋转更新 :math:`\Delta R_i` ，对于所有 :math:`i \in \{1,···,N\}` ，让等效的轴角表示表示为 :math:`\Delta \omega_i` 。

将所有这些向量放到一个  :math:`3 N \times 1`  的向量  :math:`\Delta \Omega_v = [\Delta \omega^T_1, ···, \Delta \omega^T_N]^T` 中。

对于每个残差旋转项  :math:`\Delta R_{ij}` 来说 ，所有的 :math:`(i,j)\in \epsilon` ，等效轴角表示为 :math:`\Delta \omega_{ij}` 。

所有这些向量串联成一个 :math:`3 M \times 1` 的向量表示为 :math:`\Delta \Omega_\epsilon`

那么上面的等式就等价于找到最小化成本函数 :math:`F(\Delta \Omega_v)` 的 :math:`\Delta \Omega_v` ：

.. math::

   \begin{eqnarray}
      F(\Delta \Omega_v) &=& \sum\limits_{(i,j) \in \epsilon} \rho(||\omega (R(-\Delta \omega_j)R(\Delta \omega_{ij}) R(\Delta \omega_j))||)\\
      &=& \sum\limits_{(i,j) \in \epsilon} \rho(||r_{ij} (\Delta \Omega_v)||)
   \end{eqnarray}

其中:

.. math::

   r_{ij}(\Delta \Omega_v) = \omega (R(-\Delta \omega_j)R(\Delta \omega_{ij}) R(\Delta \omega_j))

梯度 :math:`F(\Delta \Omega_v)` 由下面的式子给出：

.. math::

   \begin{eqnarray}
   \nabla F(\Delta \Omega_v) &=& \sum\limits_{(i,j) \in \epsilon} \nabla \rho(||r_{ij}(\Delta \Omega_v)||)\\
   &=& \sum\limits_{(i,j) \in \epsilon} \psi(||r_{ij} (\Delta \Omega_v)||) \nabla (||r_{ij}(\Delta \Omega_v)||)
   \end{eqnarray}

其中 :math:`\psi(r) = \frac{\partial \rho(r)}{\partial  r}` 称为 influence function。

定义 :math:`\phi(||r_{ij}(\Delta \Omega_v)||) = \frac{\psi(||r_{ij} (\Delta \Omega_v)||)}{||r_{ij} (\Delta \Omega_v)||}`

从而有：

.. math::

   \begin{eqnarray}
   && F(\Delta \Omega_v)\\
   &=& \frac{1}{2} \sum\limits_{(i,j) \in \epsilon} \phi(||r_{ij}(\Delta \Omega_v)||)2||r_{ij}(\Delta \Omega_v)|| \nabla(||r_{ij}(\Delta \Omega_v)||)\\
   &=& \frac{1}{2}  \sum\limits_{(i,j) \in \epsilon} \phi(||r_{ij}(\Delta \Omega_v)||) \nabla(||r_{ij}(\Delta \Omega_v)||^2)
   \end{eqnarray}

可以通过将 :math:`\nabla F(\Delta \Omega_v)` 等于零来找到最佳的 :math:`\Delta \Omega_v` 。

在这里，使用 **IRLS优化** ，因此，在每次迭代期间，将  :math:`\phi(||r_{ij}(\Delta \Omega_v)||)` 视为由 :math:`\phi(||r_{ij}(0)||)` 给出的常数。

记 :math:`\phi(||r_{ij}(0)||)` 为 :math:`\phi_{ij}` ，则问题变为：

.. math::

   \sum\limits_{(i,j) \in \epsilon} \phi_{ij} ·  \nabla(||r_{ij}(\Delta \Omega_v)||^2 = 0

等价于下面的最小化问题：

.. math::

   \mathop{minimize}_{\Delta \Omega_v} \sum\limits_{(i,j)\in \epsilon} \phi_{ij} ||r_{ij}(\Delta \Omega_v)||^2

权重  :math:`\phi_{ij} = \phi(||r_{ij}(0)||)` 是在每次迭代时为每条边 :math:`(i,j) \in \epsilon` 计算的。

至此，已将相对旋转平均问题简化为迭代重新加权的非线性最小二乘问题。 现在将看到如何在每次迭代中使用拟牛顿法解决加权非线性最小二乘问题。

Optimization using Quasi-Newton Method
------------------------------------------

在拟牛顿优化方法中，代价函数的 Hessian 近似为正半定矩阵。在高斯-牛顿算法的每次迭代中，函数在一阶意义上被局部逼近，因此优化问题归结为线性最小二乘问题。

方程 :math:`\sum\limits_{(i,j) \in \epsilon} \phi_{ij} ·  \nabla(||r_{ij}(\Delta \Omega_v)||^2 = 0` 等价于

.. math::

   \mathop{minimize}_{\Delta \Omega_v} \sum\limits_{(i,j) \in \epsilon} \phi_{ij} · ||r_{ij}(0) + \mathbb{J} r_{ij}(0)^T \Delta \Omega_v||^2

其中 :math:`\mathbb{J}_{ij}(0)` 是当前点 :math:`\Delta \Omega_v = 0` 处  :math:`r_{ij}(\Delta \Omega_v)`  的雅可比矩阵（相对于要估计的未知数 :math:`\Delta \Omega_v`）。

最小化上面公式中的cost等效于在最小二乘意义上求解以下线性方程组：

.. math::

   \sqrt{\phi_{ij}} \mathbb{J} r_{ij}(0)^T \Delta \Omega_v = - \sqrt{\phi_{ij}} r_{ij} (0)~~ \forall(i,j) \in \epsilon

