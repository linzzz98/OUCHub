Iteratively reweighted least squares
=====================================

迭代重加权最小二乘法 (IRLS) 用于解决某些具有 :math:`p` 范数形式的目标函数的优化问题：

.. math::

   \mathop{argmin}_{\beta} \sum\limits_{i=1}^n |y_i - f_i(\beta)|^p

（通过迭代方法）其中每个步骤都涉及解决以下形式的加权最小二乘问题：

.. math::

   \beta^{(t + 1)} = \mathop{argmin}_{\beta} \sum\limits_{i=1}^n w_i(\beta^{(t)}) |y_i - f_i(\beta)|^2

IRLS 用于找到广义线性模型的最大似然估计，并在稳健回归中找到 :math:`M` 估计量，作为减轻其他正态分布数据集中异常值影响的一种方式。

.. note::

   例如，通过最小化最小绝对误差而不是最小二乘误差。

IRLS 相对于线性规划和凸规划的优势之一是它可以与 Gauss-Newton 和 Levenberg-Marquardt 数值算法一起使用。

Example
-------

:Lp范数线性回归:

   要找到最小化线性回归问题的 :math:`L^p` 范数的参数 :math:`\beta = (\beta_1,···,\beta_k)^T`

   .. math::

      \mathop{argmin}_{\beta} ||y - X \beta||_p =  \mathop{argmin}_{\beta} \sum\limits_{i=1}^n |y_i - X_i \beta|^p

   第t + 1步的IRLS 算法涉及解决加权线性最小二乘问题：

   .. math::

      \begin{eqnarray}
      \beta^{t+1} &=& \mathop{argmin}_{\beta} \sum\limits_{i=1}^n w_i^{(t)} |y_i - X_i\beta|^2\\
      &=& (X^TW^{(t)}X)^{-1}X^TW^{(t)}y
      \end{eqnarray}

   其中 :math:`W(t)` 是权重的对角矩阵，通常所有元素最初设置为：

   .. math::

      w_i^{(0)} = 1

   并在每次迭代后更新为：

   .. math::

      w_i^{(t)} = |y_i - X_i \beta^{(t)}|^{p-2}

   在 p = 1 的情况下，这对应于最小绝对偏差回归：

   .. math::

      w_i^{(t)} = \frac{1}{|y_i-X_i \beta^{(t)}|}

   为了避免被零除，必须进行正则化，因此在实际使用中公式为：

   .. math::

      w_i^{(t)} = \frac{1}{max \{\delta,|y_i-X_i \beta^{(t)}|\}}
