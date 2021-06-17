三维重建中的旋转
=======================

.. attention::
   本篇转载自 |:point_right:|  `《三维重建中的旋转(Rotation)》 <https://zhuanlan.zhihu.com/p/62665006>`_

旋转矩阵
---------------

设某个 **单位正交基** :math:`(e_1,e_2,e_3)` 经过一次旋转变成了 :math:`(e_1',e_2',e_3')` 。那么对于同一个向量 :math:`a` （该向量没有跟随坐标系旋转而发生运动），
它在两个坐标系下的坐标为 :math:`(a_1,a_2,a_3)^T` 和  :math:`(a_1‘,a_2’,a_3‘)^T`

由坐标的定义，有：

.. math::

   \left[\begin{matrix}e_1 & e_2 & e_3\end{matrix}\right]\left[\begin{matrix}a_1\\a_2\\a_3\end{matrix}\right]=
   \left[\begin{matrix}e_1' & e_2' & e_3'\end{matrix}\right]\left[\begin{matrix}a_1'\\a_2'\\a_3'\end{matrix}\right]

   :label: eq:1

为了描述两个坐标之间的关系，上式两边同时乘 :math:`(e_1^T,e_2^T,e_3^T)^T` ，则有：

.. math::

   \left[
   \begin{matrix}
   a_1\\a_2\\a_3
   \end{matrix}
   \right] = \left[
   \begin{matrix}
   e_1^Te_1' & e_1^Te_2' & e_1^Te_3'\\
   e_2^Te_1' & e_2^Te_2' & e_2^Te_3'\\
   e_3^Te_1' & e_3^Te_2' & e_3^Te_3'\\
   \end{matrix}
   \right]\left[
   \begin{matrix}
   a_1'\\a_2'\\a_3'
   \end{matrix}
   \right] = Ra'

其中 :math:`R` 为旋转矩阵，旋转矩阵的集合定义为：

.. math::

   SO(n) = \{R \in \mathbb{R}^{n\times n} |RR^T = I,det(R) = I\}

由于旋转矩阵是正交阵，它的逆（转置）描述了相反的旋转，则有 :math:`a' = R^{-1}a = R^Ta`，即 :math:`R^T` 为相反的旋转。

李群和李代数
-----------------------

旋转空间上的李代数推导
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

设 :math:`R` 是某个相机的旋转，随时间而连续变换，即 :math:`R` 为关于时间 :math:`t` 的函数 :math:`R(t)` 。由于 :math:`R` 是正交阵，则有：

.. math::

   R(t)R(t)^T = I

等式两边对 :math:`t` 求导，则有 :math:`\frac{\partial{R(t)}}{\partial t} R(t)^T + R(t) \frac{\partial R(t)^T}{\partial t} = 0` 整理可得：

.. math::

   \frac{\partial{R(t)}}{\partial t} R(t)^T = -R(t) \frac{\partial R(t)^T}{\partial t} = -R(t)\frac{\partial R(t)^T}{\partial t} = -(\frac{\partial R(t)}{\partial t}R(t)^T)^T

由上式可以看出 :math:`\frac{\partial R(t)}{\partial t} R(t)^T` 是一个反对称矩阵（ :math:`A = -A^T`）

而对于反对称矩阵，总能找到一个三维向量 :math:`w` 与之对应。 一般的， :math:`w = [w_1,w_2,w_3]` 是一个三矢量，令 :math:`[w]_x` 表示向量到反对称阵的变换。 因此有：

.. math::

   \frac{\partial R(t)}{\partial t} R^T = [w]_x

对上面的公式，左右同时右乘 :math:`R(t)` 可得

.. math::

   \frac{\partial R(t)}{\partial t} = [w]_x R(t)

上面的公式是形如 :math:`\frac{dy}{dx} = ay` 的常微分方程，对方程两边同时取倒数，有 :math:`\frac{dx}{dy} = \frac{1}{ay}` 。显然 :math:`dx = \frac{1}{y} dy` 的解为 :math:`x = ln~ay` 进一步可得 :math:`y = e^{ax}` 。将上面的公式代入可得

.. math::

   R(t) = R(0)e^{[w]_x~t} = R(0)e^{[wt]_x}

假设 :math:`R(0) = I` ，在经过了 :math:`\Delta t` 的时间之后，此时定义向量 :math:`v \triangleq w \Delta t` ，则可以得到：

.. math::

   R = e^{[v]_x}

上式中的 :math:`v` 就是转换得到的三维旋转向量，又名旋转的轴角表示。

* 旋转向量的模表示物体绕轴逆时针旋转的角度，等于欧拉角。

* 旋转轴就是旋转向量除以模后的单位向量。

令旋转向量为 :math:`v = (v_x, v_y, v_z)^T` ，则旋转角为 :math:`\theta = norm(v)` ，旋转轴为 :math:`n = v / \theta`

**基于旋转向量的矩阵方程**

根据公式 :math:`R_{ij} = R_jR_i^{-1} ` 和 :math:`R = e^{[v]_x}` 可以用旋转向量 :math:`v` 表示全局旋转和相对旋转之间的关系：

.. math::

   e^{[v_{ij}_x]} = e^{[v_j]_x} e^{-[v_i]_x}

根据反对称矩阵的定义，可以得到：

.. math::

   v_{ij} = v_j - v_i

.. note::

   其实上面公式的确切关系是： :math:`v_{ij} = BCH(v_j, -v_i)` ，其中 :math:`BCH(.,.)` 是Baker-Campbell-Hausdorff公式

   .. math::

      BCH(x,y) = x + y + \frac{1}{2}[x,y] + \frac{1}{12}[x-y,[x,y]] + o(|(x,y)|^4)

   如果只使用BCH公式的一阶估计 :math:`BCH(x,y) \approx x + y` ，则

   .. math::

      v_{ij} = BCH(v_j, -v_i) = v_j - v_i

将上式转化为矩阵的表示形式：

.. math::

   v_{ij} = v_j - v_i = [···-I···I···] v_{global}

其中 :math:`v_{global} = [v_1, v_2, ··· , v_N]^T` 是由所有全局旋转向量组成的列向量，其中 :math:`N` 表示视图中相机的个数。此时列出所有相机对的方程并进行整合：

.. math::

   A v_{global} = v_{rel}

 :math:`v_rel` 是由根据估计的全局旋转得到的所有的相对旋转向量的列向量， :math:`v_{rel}^{x}` 是一开始计算得到的相对选择向量组成的列向量。


李代数SO（3）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

李群 :math:`SO(3)` 对应的李代数是定义在 :math:`\mathbb{R}^3` 上的向量，记为 :math:`w` 。每个 :math:`w` 都可以生成一个反对此矩阵 :math:`\Phi`

.. math::

   \Phi = [w]_x = \left[
   \begin{matrix}
   0 & -w_3 & w_2\\w_3 & 0 & -w_1\\-w_2 & w_1 & 0
   \end{matrix}
   \right] \in \mathbb{R}^{3\times 3}

一般来说， :math:`so(3)` 的元素是三维向量或者三维反对称矩阵：

.. math::

   so(3) = \{w \in R, \Phi = [w]_x \in \mathbb{R}^{3\times 3} \}

总结为： :math:`so(3)` 是一个由三维向量组成的集合，每个向量对应到一个反对称矩阵，可以表达旋转矩阵的倒数。它与 :math:`so(3)` 的关系通过指数映射给定：

.. math::

   R = exp([w]_x)

推导指数映射
~~~~~~~~~~~~~~~~~~~~~~~~~

由上面的公式 :math:`R = exp([w]_x)` 可知，其为一个矩阵的指数，在李群和李代数中，称为 **指数映射** 。

指数函数的幂级数为：

.. math::

   exp(x) = \sum\limits_{n=0}^\infty \frac{x^n}{n!}

同样的，对于 :math:`so(3)` 中的任意元素 :math:`[w]_x` ，指数映射为：

.. math::

   exp([w]_x) = \sum\limits_{n=0}^\infty \frac{([w]_x)^n}{n!}

令 :math:`w = \theta a`，其中 :math:`\theta` 为方向， :math:`a` 为长度为1的方向向量。对于 :math:`[a]_x` 由两个性质：

1.  :math:`[a]_x [a]_x = aa^T - I`

2.  :math:`[a]_x [a]_x [a]_x = -[a]_x`

利用这两个性质，可以将指数映射写成：

.. math::

   \begin{eqnarray}
   exp([w]_x) &=& exp(\theta [a]_x) = \sum\limits_{n = 0}^\infty \frac{(\theta [a]_x)^n}{n!}\\\\
   &=& I + \theta[a]_x + \frac{1}{2!} \theta^2 [a]_x [a]_x + \frac{1}{3!} \theta^3 [a]_x [a]_x [a]_x + ··· \\\\
   &=& aa^T - [a]_x [a]_x + \theta [a]_x + \frac{1}{2!} \theta^2 ([a]_x)^2 + \frac{1}{3!} \theta^3 ([a]_x)^3 + ··· \\\\
   &=& aa^T - [a]_x [a]_x + \theta [a]_x + \frac{1}{2!} \theta^2 ([a]_x)^2 - \frac{1}{3!} \theta^3 [a]_x - \frac{1}{4!}([a]_x)^2 + ··· \\\\
   &=& aa^T + (\theta - \frac{1}{3!}\theta^3 + \frac{1}{5!} \theta^5 -···)[a]_x - (1-\frac{1}{2!} \theta^2 + \frac{1}{4!}\theta^4 - ···)([a]_x)^2 \\\\
   &=& ([a]_x)^2 + I + [a]_x sin\theta - ([a]_x)^2 cos\theta \\\\
   &=& (1 - cos\theta) ([a]_x)^2 + I + [a]_x sin\theta\\\\
   &=& cos\theta I + (1-cos\theta) aa^T + [a]_x sin\theta
   \end{eqnarray}

同样可以定义 **对数映射** ，把 :math:`SO(3)` 中的元素对应到 :math:`\mathfrak{so}(3)` 中：

.. math::

   [w]_x = ln(R)^V = (\sum\limits_{n=0}^\infty \frac{(-1)^n}{n + 1} (R-I)^{n+1})^V

一般不会按照泰勒展开计算对数映射，而是通过旋转矩阵恢复李代数。

令转轴为 :math:`n` ，转角为 :math:`\theta` ，

（1）计算转角 :math:`\theta` 。对于转角 :math:`\theta` ，由罗德里格斯公式可得：

   .. math::
      \begin{eqnarray}
         tr(R) &=& cos(\theta) tr(I) + (1 - cos\theta) tr(n n^T) + sin\theta tr([n]_x) \\\\
         &=& 3cos\theta + (1-cos\theta)\\\\
         &=& 1 + 2cos\theta
      \end{eqnarray}

   因此， :math:`\theta = arccos \frac{tr(R) - 1}{2}`

（2）计算转轴 :math:`n` ，由于旋转轴上的向量在旋转后不发生改变，有 :math:`Rn = n`，因此转轴 :math:`n` 是矩阵 :math:`R` 特征值为1 对应的特征向量。 求解此方程再归一化就得到了转轴。


最后李代数可以写为 :math:`w = \theta n`


四元数
--------------

四元数拥有一个实部和三个虚部，可表示为：

.. math::

   q = (c,v) = (q_0,q_1,q_2,q_3) = q_0 + q_1 i + q_2 j + q_3 k

这三个虚部满足如下关系：

.. math::

   \begin{align*}
      & i^2 = j^2 = k^2 = -1\\\\
      & ij = k, ji = -k\\\\
      & jk = i, kj = -i\\\\
      & ki = j, ik = -j
   \end{align*}

四元数的运算
~~~~~~~~~~~~~~~~~~

设 :math:`q = (c_1, v_1), q_2 = (c_2, v_2)` ，则：

.. math::

   \begin{align*}
   & q_1 \pm q_2 = (c_1 \pm c_2, v_1 \pm v_2)\\\\
   & q_1 · q_2 = (c_1c_2 - v_1^Tv_2, c_1v_2 + c_2v_1 + v_1\times v_2)\\\\
   & ||q|| = \sqrt{q_0^2 + q_1^2 + q_2^2 + q_3^2}, q^{-1} = \frac{1}{|q|^2}(c, -v)\\\\
   & ||q_1·q_2|| = ||q_1||·||q_2||
   \end{align*}


四元数表示旋转
~~~~~~~~~~~~~~~~~~~~~~~~~~

假设旋转绕单位向量 :math:`n = (n_x, n_y, n_z)^T` 进行了角度为 :math:`\theta` 的旋转，则该旋转的四元数定义为：

.. math::

   q = (cos \frac{\theta}{2}, n_x sin \frac{\theta}{2},  n_y sin \frac{\theta}{2}, n_z sin \frac{\theta}{2})^T

令 :math:`\theta = \theta + 2\pi`， 则 :math:`q =  (-cos \frac{\theta}{2}, -n_x sin \frac{\theta}{2},  -n_y sin \frac{\theta}{2}, -n_z sin \frac{\theta}{2})^T = -q` ，即 :math:`q` 和 :math:`-q` 表示同一个旋转。

令 :math:`v = (n_x, n_y, n_z), ~ w = \theta v` 则 :math:`R = exp([w]_x)`


旋转矩阵、角轴表示法、四元数之间的转换
----------------------------------------------------

旋转矩阵与四元数
~~~~~~~~~~~~~~~~~~~~~~~

四元数->旋转矩阵

通过3.2节
