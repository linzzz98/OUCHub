|:star:| Line
==============

.. note::

   归纳总结 Multiple View Geometry in CV 里关于线的相关知识。

1. 使用向量表示线段，如 :math:`(a,b,c)^T` 表示 :math:`ax+by+c = 0`

..

2. 当且仅当 :math:`x^Tl = 0` 时，点 :math:`x` 才在线 :math:`l` 上

..

3. 自由度问题：为了指定一个点，必须提供两个值，即其x坐标和y坐标。 以类似的方式，一条线由两个参数（两个独立的比率 :math:`\{a：b：c\}` ）指定，因此具有两个自由度。在非齐次表示中，可以选择这两个参数作为直线的梯度和y截距。

..

4. 线段 :math:`l` 和 :math:`l'` 的交点 :math:`x = l \times l'`

   如  :math:`x = 1 \longrightarrow-1x+1 = 0 ~~~:~~~ l = (-1,0,1)^T`

    :math:`y = 1 \longrightarrow -1y + 1 = 0~~~:~~~ l' = (0,-1,1)^T`

    :math:`x = l\times l' = \left|\begin{matrix}i & j & k\\-1 & 0 & 1\\0 & -1 & 1\end{matrix}\right| = \left(\begin{matrix}1\\1\\1\end{matrix}\right)`

..

5. 过两个点 :math:`x` 和 :math:`x'` 的直线 :math:`l = x \times x'`

..

6. 最后一个坐标 :math:`x_3 = 0` 的点被称为理想点（ideal point），或无穷远处的点。所有的理想点都表示为 :math:`(x_1, x_2, 0)^T` ，其特定点由比率 :math:`x_1:x_2` 指定。

..

7. 无穷远线表示为 :math:`l_\infty = (0,0,1)^T` ，从而 :math:`(0,0,1)(x_1,x_2,0)^T = 0`

..

一条线由两个点的连接或两个平面的交点定义。线在3-空间中有 4 个自由度。（两个端点，一个端点两个参数）

以下是三种线的表现形式：

1. Null-space and span representation.

..

