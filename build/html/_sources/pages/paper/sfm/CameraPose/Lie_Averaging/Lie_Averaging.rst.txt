Lie-Algebraic Averaging For Globally Consistent Motion Estimation
===================================================================

一个序列的N个图像可以估计 :math:`\frac{N(N-1)}{2}` 组相对运动。

在本文使用李群结构来证明全局一致的快速运动估计算法。

Lie-Group Introduction
----------------------

在本节中，对李群进行非常基本的介绍。

群 G 是一个集合，其元素满足关系：

.. math::

   X.(Y.Z) = (X.Y).Z~~(associativity)\\

   \exists E \ni X.E = E.X = X~~(identity)\\

   \exists X^{-1} \ni X.X^{-1} = X^{-1}.X = E~~(inverse)

.. note::

   1、封闭性：群内任意两个元素或两个以上的元素（相同的或不同的）的结合（积）都是该集合的一个元素。即假设对于群G操作（运算）是 :math:`*` ，对于 :math:`G` 里的任意元素 :math:`a,b` ，那么 :math:`a*b, b*a` 都必须是 :math:`G` 的元素。

   2、结合律：虽然群元素不一定要求满足交换律，但必须满足结合律，即对 :math:`G` 中任意元素 :math:`a,b,c` 都有 :math:`(a*b)*c=a*(b*c)` 。

   3、单位元素(幺元)：集合 :math:`G` 内存在一个单位元素 :math:`e` ，它和集合中任何一个元素的积都等于该元素本身，即对于 :math:`G` 中每个元素 :math:`a` 都有  :math:`e*a = a*e = a` 。

   4、逆元素：对 :math:`G` 中每个元素 :math:`a` 在 :math:`G` 中都有元素 :math:`a^{-1}` ，使  :math:`a^{-1}*a=a*a^{-1}=e` 。

李群是一种运算 :math:`X \times Y \mapsto XY` 和 :math:`X \mapsto X^{-1}` 是可微映射的群。

李群可以在局部被视为拓扑等价于向量空间  :math:`\mathbb{R}^{n}` 。 因此，任何群元素 :math:`G` 的局部邻域都可以用它的切线空间来充分描述。

这个向量空间的元素形成李代数 :math:`g` 。 李代数 :math:`g` 是一个向量空间，配备了双线性运算 :math:`  [., .]:g × g → g`，该符号称为李括号。

.. math::

   [x,y] = -[y,x]~~(anti  − symmetry)\\
   [x,[y,z]] + [ y,[z,x]] + [z,[x,y]] = 0~~(Jacobi   identity)

所有有限维的李群都有矩阵表示，在这种情况下，括号是交换子运算  :math:`[x, y]=xy − yx` 。

李代数和相关的李群通过指数映射相关联，因此对于矩阵表示有：

.. math::

   exp(x) = \sum\limits_{k=0}^{\infty} \frac{x^k}{k!}

因此，对于角度 :math:`\omega` 的三维旋转，我们有  :math:`R(\omega) = e^{[\omega]_x}` ，其中 :math:`[\omega]_x` 是  :math:`\omega`  的反对称矩阵。

这里  :math:`R ∈ SO(3)` 是特殊正交群， :math:`[\omega]_x \in so(3)` 是相关的李代数。

从李代数到李群的逆映射也存在对数函数：

.. math::

   [\omega]_x = log(R)

稍微提及以下特殊欧几里得群 :math:`SE(3)` ，它表示旋转后平移的欧几里得变换。用 :math:`M` 和相关的李代数  :math:`m \in se(3)` 的元素来表示这个群的元素。

对于非交换李群，通常的指数关系 :math:`e^xe^y = e^{x+y}` 不成立。

等效映射由 BCH 定义： :math:`g \times g \mapsto` ，即 :math:`e^xe^y = e^{BCH(x,y)}` 。

.. note::

   BCH公式（Baker-Campbell-Hausdorff）的定义为：

   .. math::

      BCH(x,y) = x + y + \frac{1}{2} + \frac{1}{12}[x-y,[x,y]] + O(|(x,y)|^4)

注意到 BCH 公式是表示该群的流形上的内在（黎曼）距离。例如，对于旋转 :math:`\omega_1` 和 :math:`\omega_2` ， :math:`BCH(\omega_2, -\omega_1` 表示将我们从 :math:`\omega_1` 到 :math:`\omega_2` 的旋转（“距离”）。

Averaging on the Lie Group
-----------------------------

对于向量空间，集合 :math:`{X_1,···,X_N}` 的样本均值或平均值由下式给出：

.. math::

   \overline{X} = \frac{1}{N} \sum\limits_{i=1}^{N} X_i

这是“偏差”的变分最小值：

.. math::

   \sum\limits_{i=1}^N d^2(X_i,\overline{X}) = \sum\limits_{i=1}^N = (X_i - \overline{X})^2

然而，这样的概念不能直接应用于群的元素，因为群流形不等价于向量空间。 例如，两个旋转矩阵的算术平均值不一定是有效的旋转矩阵。

如果将组 :math:`G` 的元素视为嵌入在实向量空间中，则样本平均值表示为外在平均值。

在这里，该组首先嵌入到欧几里得空间  :math:`\phi : G \mapsto \mathbb{R}^n` 中，这在空间上引入了一个度量，样本平均值可以定义为：

.. math::

   \overline{\phi(X)} = \frac{1}{N} \sum\limits_{k=1}^N \phi(X_k)

然而，这个样本平均值不一定是组 G 的一个元素，因此需要以最佳的方式将它投影到流形 :math:`G` 上：

.. math::

   \overline{X} = P(\overline{\phi(X)})

另一方面，如果将 :math:`d(., .)` 定义为流形上点之间的内在距离（即黎曼距离），那么“真实”内在平均值可以定义为：

.. math::

   \mu = arg \mathop{min}\limits_{X\in G} \sum\limits_{k=1}^N d^2(X_k,X)

这里，内在平均值是通过测量群元素之间的黎曼距离来计算的，并且自动成为群 G 的元素。通常，内在平均值优于外在平均值，但由于黎曼距离函数 :math:`d(., .)` 的非线性以及需要对群流形 G 进行参数化，因此通常难以计算。

然而，对于矩阵李群，可以有效地计算内在平均值。

对于矩阵群，黎曼距离由矩阵对数运算定义，即对于矩阵群元素 :math:`X` 和 :math:`Y` ，有：

.. math::

   d(X,Y) = ||log(YX^{-1})||

使用 BCH 公式，这个距离可以近似为：

.. math::

   \begin{eqnarray}
   d(X,Y) &=& ||log(YX^{-1})||\\
   &\approx& ||log(Y) - log(X)|| = ||y - x||
   \end{eqnarray}

其中 :math:`x,y` 分别是矩阵 :math:`X,Y` 的对数。

因此，李群元素之间的黎曼距离现在近似于其李代数中的“欧几里得”距离，即它的切线空间近似。

对于一组群元素  :math:`\{X1 , ··· , XN \}` ， :math:`\sum\limits_{i=1}^N||X_i - \overline{X}||` 的最小值是从李代数  :math:`{x_1 , ··· , x_N }` 的样本平均值估计的。

鉴于平均值 :math:`\mu = \frac{1}{N} \sum\limits_{i=1}^N x_i` 的估计，可以通过左乘 :math:`\mu` 的倒数来重新映射样本。

换句话说，有  :math:`\Delta X_i \leftarrow \mu^{-1} X_i` ，粗略地说，它是“减去” :math:`\mu` 后原始样本的残差。

这个操作可以重复直到估计收敛到局部最小值。

:Algorithm 1:

   .. figure:: 1.jpg
      :figclass: algin-center
      :scale: 70%

此迭代在本质上类似于梯度下降算法，并且始终收敛到局部最小值。

也可以在每次迭代的估计中使用 BCH 公式的高阶项，从而产生更复杂的公式，这是更好的近似。 然而，这并不影响固定点的位置。

Lie Algebras of SO(3) and SE(3)
---------------------------------

任何三维旋转 :math:`R` 都是特殊正交群 :math:`SO(3)` 的一个元素，并且满足约束 :math:`RR^T = I` 。

指数和对数映射由熟悉的 Rodrigues 公式给出。（略）

对于旋转  :math:`\omega_1,\omega_2` ，BCH 形式由  :math:`BCH(\omega_1,\omega_2) = \alpha \omega_1 + \beta \omega_2 + \gamma \omega_1 \times \omega_2` 给出，其中标量  :math:`\alpha, \beta, \gamma` 是 :math:`\omega_1` 和 :math:`\omega_2` 的函数。

因此，在旋转内在平均的算法中，不需要在每次迭代时计算对数和指数。 相反，可以直接在李代数中进行，直到算法终止，这会导致更快的计算。

欧式运动 :math:`M\in SE(3)`  由 :math:`4 \times 4` 矩阵表示：

.. math::

   M = \left[
   \begin{matrix}
   R & t\\0 & 1
   \end{matrix}
   \right]

其中  :math:`R \in SO(3)` 和  :math:`t \in \mathbb{R}^3` 分别是三维旋转和平移。

**此变换的流程是先旋转，然后进行平移。**

 :math:`M` 的对数是李代数  :math:`m \in se(3)` 的一个元素，由下式给出：

.. math::

   m = \left[
   \begin{matrix}
   \Omega & u \\0 & 0
   \end{matrix}
   \right]

其中反对称矩阵  :math:`\Omega \in so(3)` 和  :math:`\mu \in \mathbb{R}^3` 。

由于指数映射将 :math:`m` 与矩阵 :math:`M` 相关联，有：

.. math::

   M = exp(m) = \sum\limits_{k=0}^\infty \frac{m^k}{k!} = \left[
   \begin{matrix}
   R & t\\0 & 1
   \end{matrix}
   \right]

通过这一系列表达式，可以证明以下关系成立：

.. figure:: 2.jpg
   :figclass: align-center
   :scale: 75%