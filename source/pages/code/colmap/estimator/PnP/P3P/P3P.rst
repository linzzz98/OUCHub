.. default-domain:: cpp

P3P
=====


P3P(透视三点)问题的解析求解器。

.. parsed-literal::

    \ `Complete Solution Classification for the Perspective-Three-Point Problem <http://www.mmrc.iss.ac.cn/~xgao/paper/ieee.pdf>`_

成员变量
~~~~~~~~~~~

1. 2D图像特征观察值

    :cpp:type:`X_t`

2. 世界框架中观察到的3D特征

    :cpp:type:`Y_t`

3. 从世界到相机框架的转变

    :cpp:type:`M_t`

4. 估计模型所需的最少样本数

    :cpp:member:`kMinNumSamples`

成员函数
~~~~~~~~~~~

1. **LiftImagePoint**

向量单位化

.. cpp:function:: Eigen::Vector3d LiftImagePoint(const Eigen::Vector2d& point)

.. code-block:: cpp

    return point.homogeneous() / std::sqrt(point.squaredNorm() + 1);

假设point为\ :math:`(x,y)`\ ，则point.homogeneous()为\ :math:`(x,y,1)`\ ，单位化后为：\ :math:`(x,y, 1) / \sqrt{(x^2 + y^2 +1)}`

2. **Estimate**

从一组三个2D-3D点对应关系中估计P3P问题的最可能解决方案

-  @param points2D Normalized 2D image points as 3x2 matrix.

-  @param points3D 3D world points as 3x3 matrix.

-  @return Most probable pose as length-1 vector of a 3x4 matrix.

.. cpp:function:: std::vector P3PEstimator::Estimate( const std::vector& points2D, const std::vector& points3D)

.. code-block:: cpp

     CHECK_EQ(points2D.size(), 3);
     CHECK_EQ(points3D.size(), 3);

     Eigen::Matrix3d points3D_world;
     points3D_world.col(0) = points3D[0];
     points3D_world.col(1) = points3D[1];
     points3D_world.col(2) = points3D[2];

     // 得到单位化的图像坐标(u,v,w)
     const Eigen::Vector3d u = LiftImagePoint(points2D[0]);
     const Eigen::Vector3d v = LiftImagePoint(points2D[1]);
     const Eigen::Vector3d w = LiftImagePoint(points2D[2]);

     // Angles between 2D points.
     const double cos_uv = u.transpose() * v;
     const double cos_uw = u.transpose() * w;
     const double cos_vw = v.transpose() * w;

     // Distances between 2D points.
     const double dist_AB_2 = (points3D[0] - points3D[1]).squaredNorm();
     const double dist_AC_2 = (points3D[0] - points3D[2]).squaredNorm();
     const double dist_BC_2 = (points3D[1] - points3D[2]).squaredNorm();

     const double dist_AB = std::sqrt(dist_AB_2);

     const double a = dist_BC_2 / dist_AB_2;
     const double b = dist_AC_2 / dist_AB_2;

     // Helper variables for calculation of coefficients.
     const double a2 = a * a;
     const double b2 = b * b;
     const double p = 2 * cos_vw;
     const double q = 2 * cos_uw;
     const double r = 2 * cos_uv;
     const double p2 = p * p;
     const double p3 = p2 * p;
     const double q2 = q * q;
     const double r2 = r * r;
     const double r3 = r2 * r;
     const double r4 = r3 * r;
     const double r5 = r4 * r;

     // Build polynomial coefficients: a4*x^4 + a3*x^3 + a2*x^2 + a1*x + a0 = 0.
     Eigen::Matrix<double, 5, 1> coeffs;
     coeffs(0) = -2 * b + b2 + a2 + 1 + a * b * (2 - r2) - 2 * a;

     coeffs(1) = -2 * q * a2 - r * p * b2 + 4 * q * a + (2 * q + p * r) * b
                 + (r2 * q - 2 * q + r * p) * a * b - 2 * q;

     coeffs(2) = (2 + q2) * a2 + (p2 + r2 - 2) * b2 - (4 + 2 * q2) * a -
                 (p * q * r + p2) * b - (p * q * r + r2) * a * b + q2 + 2;

     coeffs(3) = -2 * q * a2 - r * p * b2 + 4 * q * a + (p * r + q * p2 - 2 * q)
                 * b + (r * p + 2 * q) * a * b - 2 * q;

     coeffs(4) = a2 + b2 - 2 * a + (2 - p2) * b - 2 * a * b + 1;

     Eigen::VectorXd roots_real;
     Eigen::VectorXd roots_imag;

     if (!FindPolynomialRootsCompanionMatrix(coeffs, &roots_real, &roots_imag)) {
       return std::vector<P3PEstimator::M_t>({});
     }

     std::vector<M_t> models;
     models.reserve(roots_real.size());

     for (Eigen::VectorXd::Index i = 0; i < roots_real.size(); ++i) {
       const double kMaxRootImag = 1e-10;
       if (std::abs(roots_imag(i)) > kMaxRootImag) {
         continue;
       }

       const double x = roots_real(i);
       if (x < 0) {
         continue;
       }

       const double x2 = x * x;
       const double x3 = x2 * x;

       // Build polynomial coefficients: b1*y + b0 = 0.
       const double bb1 =
           (p2 - p * q * r + r2) * a + (p2 - r2) * b - p2 + p * q * r - r2;
       const double b1 = b * bb1 * bb1;
       const double b0 =
           ((1 - a - b) * x2 + (a - 1) * q * x - a + b + 1) *
           (r3 * (a2 + b2 - 2 * a - 2 * b + (2 - r2) * a * b + 1) * x3 +
            r2 *
                (p + p * a2 - 2 * r * q * a * b + 2 * r * q * b - 2 * r * q -
                 2 * p * a - 2 * p * b + p * r2 * b + 4 * r * q * a +
                 q * r3 * a * b - 2 * r * q * a2 + 2 * p * a * b + p * b2 -
                 r2 * p * b2) *
                x2 +
            (r5 * (b2 - a * b) - r4 * p * q * b +
             r3 * (q2 - 4 * a - 2 * q2 * a + q2 * a2 + 2 * a2 - 2 * b2 + 2) +
             r2 * (4 * p * q * a - 2 * p * q * a * b + 2 * p * q * b - 2 * p * q -
                   2 * p * q * a2) +
             r * (p2 * b2 - 2 * p2 * b + 2 * p2 * a * b - 2 * p2 * a + p2 +
                  p2 * a2)) *
                x +
            (2 * p * r2 - 2 * r3 * q + p3 - 2 * p2 * q * r + p * q2 * r2) * a2 +
            (p3 - 2 * p * r2) * b2 +
            (4 * q * r3 - 4 * p * r2 - 2 * p3 + 4 * p2 * q * r - 2 * p * q2 * r2) *
                a +
            (-2 * q * r3 + p * r4 + 2 * p2 * q * r - 2 * p3) * b +
            (2 * p3 + 2 * q * r3 - 2 * p2 * q * r) * a * b + p * q2 * r2 -
            2 * p2 * q * r + 2 * p * r2 + p3 - 2 * r3 * q);

       // Solve for y.
       const double y = b0 / b1;
       const double y2 = y * y;

       const double nu = x2 + y2 - 2 * x * y * cos_uv;

       const double dist_PC = dist_AB / std::sqrt(nu);
       const double dist_PB = y * dist_PC;
       const double dist_PA = x * dist_PC;

       Eigen::Matrix3d points3D_camera;
       points3D_camera.col(0) = u * dist_PA;  // A'
       points3D_camera.col(1) = v * dist_PB;  // B'
       points3D_camera.col(2) = w * dist_PC;  // C'

       // Find transformation from the world to the camera system.
       const Eigen::Matrix4d transform =
           Eigen::umeyama(points3D_world, points3D_camera, false);
       models.push_back(transform.topLeftCorner<3, 4>());
     }

     return models;

.. note::

    证明：

    .. figure:: 1.png
        :figclass: align-center

    令

    .. math::

        |PA| = X, ~~|PB| = Y, ~~|PC|=Z,\\\\

        \alpha = \angle BPC,~~ \beta = \angle APC,~~ \gamma = \angle APC,\\\\

        p = 2cos\alpha, ~~q = 2cos\beta, ~~r = 2cos\gamma

    .. code-block:: cpp

        const double cos_uv = u.transpose() * v; // cos_uv = r / 2 ==> θ(uv) = θ(γ)
        const double cos_uw = u.transpose() * w; // cos_uw = q / 2 ==> θ(uw) = θ(β)
        const double cos_vw = v.transpose() * w; // cos_vw = p / 2 ==> θ(vw) = θ(α)

        const double dist_AB_2 = (points3D[0] - points3D[1]).squaredNorm();     //AB^2
        const double dist_AC_2 = (points3D[0] - points3D[2]).squaredNorm();     //AC^2
        const double dist_BC_2 = (points3D[1] - points3D[2]).squaredNorm();     //BC^2

        const double dist_AB = std::sqrt(dist_AB_2);                            //AB

        const double p = 2 * cos_vw;    // p
        const double q = 2 * cos_uw;    // q
        const double r = 2 * cos_uv;    // r
        const double p2 = p * p;        // p^2
        const double p3 = p2 * p;       // p^3
        const double q2 = q * q;        // q^2
        const double r2 = r * r;        // r^2
        const double r3 = r2 * r;       // r^3
        const double r4 = r3 * r;       // r^4
        const double r5 = r4 * r;       // r^5

    从三角形\ :math:`PBC`\ ，\ :math:`PAC`\ 和\ :math:`PAB`\ 中获得P3P方程组：(1)

    .. figure:: 2.png
        :figclass: align-center


    为了简化方程组，令\ :math:`X = xZ`\ ，\ :math:`Y=yZ`\ ，\ :math:`|AB| = \sqrt{v}Z`\ ，\ :math:`|BC| = \sqrt{av}Z`\ ，\ :math:`|AC| = \sqrt{bv}Z`\ ，因为\ :math:`Z = |PC| \ne 0`\ ，可以得到下面的方程组：(3)

    .. code-block:: cpp

        const double a = dist_BC_2 / dist_AB_2; //|BC| = \sqrt{a} |AB| ==> a = |BC|^2 - |AB|^2
        const double b = dist_AC_2 / dist_AB_2; //|AC| = \sqrt{b} |AB| ==> b = |AC|^2 - |AB\^2

        const double a2 = a * a;                // a^2
        const double b2 = b * b;                // b^2

    .. figure:: 3.png
        :figclass: align-center


    因为\ :math:`|r| < 2`\ ，可以得到\ :math:`v = x^2 + y^2 -xyr > 0`\ ，因此\ :math:`Z`\ 可以被表示为\ :math:`Z = |AB| / \sqrt{v}`\ ，由上面的式子消去\ :math:`v`\ ，可以得到：(ES)

    .. figure:: 4.png
        :figclass: align-center


    参考Wu-Ritt的零分解方法，将多项式方程组的零集表示为三角形式的方程组的并集。

    .. figure:: 5.png
        :figclass: align-center


    其中：

    .. figure:: 6.png
        :figclass: align-center


    .. code-block:: cpp

        Eigen::Matrix<double, 5, 1> coeffs;

        coeffs(0) = -2 * b + b2 + a2 + 1 + a * b * (2 - r2) - 2 * a;                 // a0

        coeffs(1) = -2 * q * a2 - r * p * b2 + 4 * q * a + (2 * q + p * r) * b +     // a1
                    (r2 * q - 2 * q + r * p) * a * b - 2 * q;

        coeffs(2) = (2 + q2) * a2 + (p2 + r2 - 2) * b2 - (4 + 2 * q2) * a -          // a2
                    (p * q * r + p2) * b - (p * q * r + r2) * a * b + q2 + 2;

        coeffs(3) = -2 * q * a2 - r * p * b2 + 4 * q * a +                           // a3
                    (p * r + q * p2 - 2 * q) * b + (r * p + 2 * q) * a * b - 2 * q;

        coeffs(4) = a2 + b2 - 2 * a + (2 - p2) * b - 2 * a * b + 1;                  // a4

    接下来，需要求解该方程：

    .. math::

       a_0x^4 + a_1x^3+a_2x^2+a_3x+a_4 = 0

    源码中作者使用了伴随矩阵的找到多项式的根，具体如下：

    对于多项式，\ :math:`\sum_{i=0}^N polynomial(i) x^{N-i}.`\ ，通过找到伴随矩阵

    .. math::


       A = \left[
       \begin{matrix}
       -a_{n-1} & -a_{n-2} & ··· & -a_0\\
       1 & 0 & ··· & 0\\
        & 1 & \ddots\\
        0 & \ddots  & 1 & 0
       \end{matrix}
       \right]

    通过求解矩阵\ :math:`Ax = \lambda x`\ 的特征值，进而计算出\ :math:`x`\ 。

    .. code-block:: cpp

        bool FindPolynomialRootsCompanionMatrix(const Eigen::VectorXd& coeffs_all, Eigen::VectorXd* real, Eigen::VectorXd* imag) {

        CHECK_GE(coeffs_all.size(), 2);

        Eigen::VectorXd coeffs = RemoveLeadingZeros(coeffs_all);

        const int degree = coeffs.size() - 1;

        if (degree <= 0) { return false; }

        else if (degree == 1) { return FindLinearPolynomialRoots(coeffs, real, imag); }

        else if (degree == 2) { return FindQuadraticPolynomialRoots(coeffs, real, imag); }

        // 删除系数为零的解
        coeffs = RemoveTrailingZeros(coeffs);

        // 检查是否只有零解
        if (coeffs.size() == 1) { if (real != nullptr) {

        real->resize(1); (*real)(0) = 0; } if (imag != nullptr) {

        imag->resize(1); (*imag)(0) = 0; } return true; }

        // 填充伴随矩阵C =====> 构造A
        Eigen::MatrixXd C(coeffs.size() - 1, coeffs.size() - 1);

        C.setZero();

        for (Eigen::MatrixXd::Index i = 1; i < C.rows(); ++i) { C(i, i - 1) = 1; }

        C.row(0) = -coeffs.tail(coeffs.size() - 1) / coeffs(0);

        // 求解多项式的根
        // false指不需要求特征向量
        //Eigen::EigenSolver<_MatrixType >::EigenSolver (const EigenBase< InputType > & matrix,bool computeEigenvectors = true)

        Eigen::EigenSolver solver(C, false);

        if (solver.info() != Eigen::Success) { return false; }

        // 如果后面有0，则必须添加零作为解
        const int effective_degree = coeffs.size() - 1 < degree ? coeffs.size() : coeffs.size() - 1;

        // 求解实数解
        if (real != nullptr) {

        real->resize(effective_degree);

        real->head(coeffs.size() - 1) = solver.eigenvalues().real();

        if (effective_degree > coeffs.size() - 1) { (*real)(real->size() - 1) = 0; }}

        // 求解虚数解
        if (imag != nullptr) {

        imag->resize(effective_degree);

        imag->head(coeffs.size() - 1) = solver.eigenvalues().imag();

        if (effective_degree > coeffs.size() - 1) {

        (*imag)(imag->size() - 1) = 0; } }

        return true; }

    参考：

    《R. A. Horn & C. R. Johnson, Matrix Analysis. Cambridge, UK: Cambridge University Press, 1999, pp. 146 3.3.11， 149 11》

    《X.S. Gao, X.-R. Hou, J. Tang, H.-F. Chang. Complete Solution Classification for the Perspective-Three-Point Problem.》

    回到P3P源码：

    .. code-block:: cpp

        // 求解多项式f1的实数解和虚数解
        Eigen::VectorXd roots_real;

        Eigen::VectorXd roots_imag;

        if (!FindPolynomialRootsCompanionMatrix(coeffs, &roots_real, &roots_imag))

        {     return std::vector<P3PEstimator::M_t>({});   }

    遍历每一个实数根

    .. code-block:: cpp

        for (Eigen::VectorXd::Index i = 0; i < roots_real.size(); ++i)

    计算\ :math:`x^2,x^3`

    .. code-block:: cpp

        const double x2 = x * x;

        const double x3 = x2 * x;

    .. figure:: 7.png
        :figclass: align-center


    注意，源码中将b0 * y - b1的形式改成了b1 * y - b0 = 0. 本质是一样的

    .. code-block:: cpp

        const double bb1 =  (p2 - p * q * r + r2) * a + (p2 - r2) * b - p2 + p * q * r - r2;
        const double b1 = b * bb1 * bb1;
        const double b0 =
           ((1 - a - b) * x2 + (a - 1) * q * x - a + b + 1) *
           (r3 * (a2 + b2 - 2 * a - 2 * b + (2 - r2) * a * b + 1) * x3 +
            r2 *
                (p + p * a2 - 2 * r * q * a * b + 2 * r * q * b - 2 * r * q -
                 2 * p * a - 2 * p * b + p * r2 * b + 4 * r * q * a +
                 q * r3 * a * b - 2 * r * q * a2 + 2 * p * a * b + p * b2 -
                 r2 * p * b2) *
                x2 +
            (r5 * (b2 - a * b) - r4 * p * q * b +
             r3 * (q2 - 4 * a - 2 * q2 * a + q2 * a2 + 2 * a2 - 2 * b2 + 2) +
             r2 * (4 * p * q * a - 2 * p * q * a * b + 2 * p * q * b - 2 * p * q -
                   2 * p * q * a2) +
             r * (p2 * b2 - 2 * p2 * b + 2 * p2 * a * b - 2 * p2 * a + p2 +
                  p2 * a2)) *
                x +
            (2 * p * r2 - 2 * r3 * q + p3 - 2 * p2 * q * r + p * q2 * r2) * a2 +
            (p3 - 2 * p * r2) * b2 +
            (4 * q * r3 - 4 * p * r2 - 2 * p3 + 4 * p2 * q * r - 2 * p * q2 * r2) *
                a +
            (-2 * q * r3 + p * r4 + 2 * p2 * q * r - 2 * p3) * b +
            (2 * p3 + 2 * q * r3 - 2 * p2 * q * r) * a * b + p * q2 * r2 -
            2 * p2 * q * r + 2 * p * r2 + p3 - 2 * r3 * q);

    求解\ :math:`y` (\ :math:`y = b0 / b1`\ )

    .. code-block:: cpp

        const double y = b0 / b1;      // y

        const double y2 = y * y;       // y^2

    求解\ :math:`v`\ (\ :math:`v = x^2 + y^2 - 2xycos(\gamma))`

    .. code-block:: cpp

        const double nu = x2 + y2 - 2 * x * y * cos_uv;

    求解
    :math:`PC(Z),PB(Y),PA(X)`\ (\ :math:`Z = |AB| / \sqrt{v}， Y = yZ, X = xZ`\ )

    .. code-block:: cpp

        const double dist_PC = dist_AB / std::sqrt(nu);

        const double dist_PB = y * dist_PC;

        const double dist_PA = x * dist_PC;

    计算相机位姿：

    .. code-block:: cpp

        Eigen::Matrix3d points3D_camera;

        points3D_camera.col(0) = u * dist_PA;  // A'

        points3D_camera.col(1) = v * dist_PB;  // B'

        points3D_camera.col(2) = w * dist_PC;  // C'

    寻找从世界到相机系统的转换：

    .. code-block:: cpp

        const Eigen::Matrix4d transform = Eigen::umeyama(points3D_world, points3D_camera, false);

        models.push_back(transform.topLeftCorner<3, 4>());

    这里的Eigen::umeyama计算出两组数据间的旋转与平移矩阵。

    目标：计算一组R、t使目标函数最优：

    .. figure:: 8.png
        :figclass: align-center


    最终的判断标准是距离的平方和，也就是一个最小二乘估计问题。

    最终计算结果为：

    .. figure:: 9.png
        :figclass: align-center


    其中\ :math:`c`\ 是一个缩放系数。(当第三个参数取值为false时，c = 1)

3. **Residuals**

给定一组2D-3D点对应关系和一个投影矩阵，计算平方的重新投影误差

-  @param points2D Normalized 2D image points as Nx2 matrix.

-  @param points3D 3D world points as Nx3 matrix.

-  @param proj\_matrix 3x4 projection matrix.

-  @param residuals Output vector of residuals.

.. cpp:function:: void P3PEstimator::Residuals(const std::vector<X_t>& points2D, const std::vector<Y_t>& points3D, const M_t& proj_matrix, std::vector<double>* residuals)

.. code-block:: cpp

    ComputeSquaredReprojectionError(points2D, points3D, proj_matrix, residuals);
