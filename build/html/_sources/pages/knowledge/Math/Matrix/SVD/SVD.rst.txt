.. |n| replace:: :math:`n`
.. |m| replace:: :math:`m`
.. |A| replace:: :math:`A`
.. |v| replace:: :math:`v`
.. |x| replace:: :math:`x`
.. |ATA| replace:: :math:`A^TA`
.. |AAT| replace:: :math:`AA^T`
.. |nxn| replace:: :math:`n \times n`
.. |mxm| replace:: :math:`m \times m`

SVD奇异值分解
==================

.. attention::
   本篇部分参考自 |:point_right:|  `《奇异值分解（SVD）》 <https://zhuanlan.zhihu.com/p/29846048>`_


特征值和特征向量
---------------------------------------
特征值和特征向量的定义如下：

.. math::

   Ax = \lambda x

其中 :math:`A` 一个 :math:`n \times n` 的矩阵，  :math:`x` 是一个  :math:`n`  维向量， 则 :math:`\lambda` 是矩阵 :math:`A` 的一个特征值，而 :math:`x` 是矩阵 :math:`A` 的特征值 :math:`\lambda` 所对应的特征向量。

.. note::

   一个矩阵乘以一个向量后得到的向量，其实就相当于将这个向量进行了线性变换。

   特征值所对应的特征向量就是描述这个矩阵变化方向，特征值越大的说明变化方向越主要。

特征分解
---------------------------------

求出特征值和特征向量的好处在于可以将矩阵 :math:`A` 进行特征分解。

如果求出了矩阵 :math:`A` 的 :math:`n` 个特征值 :math:`\lambda_1 \le \lambda_2 \le ... \lambda_n` 以及这 :math:`n` 个特征值所对应的特征向量 :math:`w_1, w_2, ..., w_n`

那么矩阵 :math:`A` 就可以用下面的特征分解表示

.. math::

   A = W \Sigma W^{-1}

其中 :math:`W` 是这 :math:`n` 个特征向量所组成的 :math:`n \times n` 维矩阵，而 :math:`\Sigma` 是这 :math:`n` 个特征值为主对角线的 :math:`n \times n` 维矩阵。

一般我们会把 :math:`W` 的这 :math:`n` 个特征向量标准化，即满足 :math:`||w_i||_2 = 1` ，或者 :math:`w_i^Tw_i = 1` ，此时 :math:`W` 的 :math:`n` 个特征向量称为标准正交基，满足 :math:`W^TW = I` ， 即 :math:`W^T = W^{-1}` ，也就是说 :math:`W` 是酉矩阵。

这样特征分解表达式可以写成

.. math::

   A = W \Sigma W^T

.. important::

   注意到要进行特征分解，矩阵A必须为方阵。

   那么如果A不是方阵，即行和列不相同时，还可以对矩阵进行分解吗？ |:point_right:| SVD 分解


SVD分解
-----------------------------------

.. tip::

   SVD也是对矩阵进行分解，但是和特征分解不同，SVD并不要求要分解的矩阵为方阵。

假设矩阵A是一个 :math:`m \times n` 的矩阵，那么定义矩阵A的SVD为：

.. math::

   A = U \Sigma V^T

其中 :math:`U`  是一个  :math:`m \times m` 的矩阵， :math:`V` 是一个  :math:`n \times n` 的矩阵， :math:`U` 和  :math:`V` 都是酉矩阵， 满足：

.. math::

   \begin{eqnarray}
   U^TU &=& I\\
   V^TV &=& I
   \end{eqnarray}

:math:`\Sigma` 是一个  :math:`m \times n` 的矩阵，主对角线上的每个元素都称为奇异值：

.. math::

   \Sigma = \left[
   \begin{matrix}
   \Sigma_1 & 0\\0 & 0
   \end{matrix}
   \right]

且 :math:`\Sigma_1 = diag(\sigma_1,\sigma_2,...,\sigma_r)` ，对角线按照顺序 :math:`\sigma_1 \ge \sigma_2 \ge \sigma_r > 0` ，其中 :math:`r = Rank(A)`

.. figure:: 1.jpg
   :figclass: align-center

.. important::

    SVD 分解 相当于将 :math:`M` 的线性变换分解为 旋转（ :math:`U` ） 、拉伸（ :math:`\Sigma` ）、旋转（ :math:`V^T` ）

.. tip::
   如何求出SVD分解后的 :math:`U, \Sigma, V^T` 这三个矩阵呢？ |:sweat_smile:|

   将 :math:`A^T` 和 :math:`A` 做矩阵乘法，那么会得到 :math:`n \times n` 的一个方阵 :math:`A^TA`

   注意到 |ATA| 是方阵， 那么可以进行特征分解。

   将 :math:`A` 和 :math:`A^T` 做矩阵乘法，那么会得到 |mxm| 的一个方阵 |AAT|

   注意到 |AAT| 是方阵， 那么可以进行特征分解。

分解 |ATA| 得到特征值和特征向量满足下式：

.. math::

   (A^TA)v_i = \lambda_i v_i

这样就可以得到矩阵 :math:`A^TA` 的 :math:`n` 个特征值和对应的  :math:`n` 个特征向量 :math:`v` 了。

将 :math:`A^TA` 的所有特征向量组成一个 |n| 的矩阵 :math:`V^T` ，就是SVD公式里的 :math:`V^T` 矩阵。

.. important::

   一般把  :math:`V^T` 中的每个特征向量叫做 |A| 的右奇异向量

分解 |AAT| 得到特征值和特征向量满足下式：

.. math::

   (AA^T)u_i = \lambda_i u_i

这样可以得到矩阵 |AAT| 的 |m| 个特征值和对应的 |m| 个特征向量  :math:`u` 了。

将 |AAT| 的所有特征向量组成一个 |m| 的矩阵 :math:`U` ，就是SVD公式里的 :math:`U` 矩阵。

.. important::

   一般把  :math:`U` 中的每个特征向量叫做 |A| 的左奇异向量

由于 :math:`\Sigma` 除了对角线上是奇异值其他位置都是0，那我们只需要求出每个奇异值 :math:`\sigma` 就可以了。

注意到：

.. math::

   A = U\Sigma V^T \Rightarrow AV = U\Sigma V^T V \Rightarrow AV = U\Sigma \Rightarrow Av_i = \sigma_i u_i \Rightarrow \sigma_i = A v_i / u_i

这样我们可以求出我们的每个奇异值，进而求出奇异值矩阵 :math:`\Sigma`

.. note::
   之前说 |ATA| 的特征向量组成的矩阵就是  :math:`V^T`  矩阵，|AAT| 的特征向量组成的就是 :math:`U` 矩阵， 依据是什么？

   以  :math:`V` 矩阵的证明为例：

   .. math::

      A = U\Sigma V^T \Rightarrow A^T = V\Sigma U^T \Rightarrow A^TA = V\Sigma U^TU \Sigma V^T = V \Sigma^2 V^T

   上式证明使用了 :math:`U U^T = I` ，  :math:`\Sigma ^T = \Sigma`

   可以看出 |ATA| 的特征向量组成的的确就是SVD中的  :math:`V^T` 矩阵。类似的方法可以得到 |AAT| 的特征向量组成的就是SVD中的 :math:`U` 矩阵。

.. important::

   进一步还可以看出特征值矩阵等于奇异值矩阵的平方，也就是说特征值和奇异值满足如下关系：

   .. math::

      \sigma_i = \sqrt{\lambda_i}

   这样也就是说，可以不用  :math:`\sigma_i = \frac{A v_i}{u_i}` 计算奇异值，也可以通过求出 |ATA| 的特征值取平方根来求奇异值。

SVD求解线性方程
-----------------------------------------
形式为 :math:`Ax = b` 的方程组。 设 :math:`A` 为 :math:`m \times n` 矩阵，有以下三种情况：

1. 如果m < n，则未知数多于方程式。 在这种情况下，将没有唯一的解，而是解的向量空间。
2. 如果m = n，只要A可逆，就有唯一解。
3. 如果m > n，则方程式多于未知数。 一般认为没有解。



SVD分解的意义
------------------------------------------

.. important::

   在奇异值矩阵中奇异值是按照从大到小排列，而且奇异值的减少特别的快，在很多情况下，前10%甚至1%的奇异值的和就占了全部的奇异值之和的99%以上的比例。

   也就是说，可以用最大的k个的奇异值和对应的左右奇异向量来近似描述矩阵。

   .. math::

      A_{m \times n} = U_{m \times m} \Sigma_{m \times n} V_{n \times n}^T \approx U_{m \times k} \Sigma_{k \times k} V^T_{k \times n}

   其中 :math:`k` 要比 |n| 小很多，也就是一个大的矩阵 |A| 可以用三个小的矩阵  :math:`U_{m\times k}`、 :math:`\Sigma_{k \times k}`、  :math:`V^T_{k \times n}` 来表示。

   .. figure:: 2.jpg
      :figclass: align-center

SVD分解后，矩阵 |A| 可以展开成：

.. math::

   A = \sigma_1 u_1 v_1^T + \sigma_2 u_2 v_2^T + ... + s_k u_k v_k^T (k < n)

其中等式右边每一项前的系数 :math:`\sigma` 就是奇异值， :math:`u` 和  :math:`v` 分别表示列向量， 每一项 :math:`uv^T` 都是秩为1的矩阵。 假定奇异值满足： :math:`\sigma_1 \ge \sigma_2 \ge ... \ge \sigma_r > 0`

SVD应用就是图像压缩存储，因为数字图像本身就是个矩阵，通过上面所说的近似的低秩小矩阵替代原矩阵，可以大大减少存储量

.. figure:: 3.jpg
   :figclass: align-center

可以看到上面的图像中，只保留第一项 :math:`A_1 = \sigma_1 u_1 v_1^T` ，作图为  :math:`k = 1` 看不清楚是什么图像。

随着不断的添加项进来 :math:`A_5 = \sigma_1 u_1 v_1^T + \sigma_2 u_2 v_2^T + \sigma_3 u_3 v_3^T + \sigma_4 u_4 v_4^T + \sigma_5 u_5 v_5^T`，
基本可以辨别图像的模糊特征。

当奇异值个数 :math:`k = 30` 时基本与原图差别不大了，即当 :math:`k = 1` 不断增大时，  :math:`A_k` 不断逼近  :math:`A`，但存储量却大大下降了。

.. note::

   用低秩矩阵代替原矩阵，在效果没有太大差别的情况下，大大减少了存储量，从而实现了图像的压缩存储。


**附录1 SVD压缩存储数字图像MATLAB代码：**

.. code-block:: matlab

   grayValue = imread('1.jpg');
   grayValue = rgb2gray(grayValue);
   grayValue = im2double(grayValue);
   [m, n]= size(grayValue);
   %%
   % 奇异值分解
   nr = 30; %保留的秩数
   [u, s, v] = svd(grayValue);
   grayValue2 = u(:,1:nr)*s(1:nr,1:nr)*v(:,1:nr)';
   grayValue2 = grayValue2*255;
   grayValue2 = uint8(grayValue2);
   figure
   subplot(1,2,1)
   imshow(grayValue)
   title('原图')
   subplot(1,2,2)
   imshow(grayValue2)
   title(['秩r=',num2str(nr)])
   imwrite(grayValue2,'r30.jpg')
