from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from numpy import asarray
from numpy import sqrt
from numpy import mean
from numpy import sum
from numpy import zeros
from numpy.linalg import lstsq

from scipy.linalg import svd
from scipy.optimize import leastsq

# should this not be defined in a different location?
from compas.geometry import local_coords_numpy
from compas.geometry import global_coords_numpy

from compas.numerical import pca_numpy


__all__ = [
    'bestfit_plane_numpy',
    'bestfit_circle_numpy',
    'bestfit_sphere_numpy',
]


def bestfit_plane_numpy(points):
    """Fit a plane through more than three (non-coplanar) points.

    Warning
    -------
    This function requires Numpy and Scipy.

    Parameters
    ----------
    points : list
        XYZ coordinates of the points.

    Returns
    -------
    tuple
        A point on the plane, and the normal vector.

    Examples
    --------
    .. code-block:: python

        #

    """
    xyz = asarray(points).reshape((-1, 3))
    n = xyz.shape[0]
    m = 1.0 / (n - 1.0)
    c = (sum(xyz, axis=0) / n).reshape((-1, 3))
    Yt = xyz - c
    C = m * Yt.T.dot(Yt)
    u, s, vT = svd(C)
    w = vT[2, :]
    return c, w


# # @see: https://stackoverflow.com/questions/35070178/fit-plane-to-a-set-of-points-in-3d-scipy-optimize-minimize-vs-scipy-linalg-lsts
# # @see: https://stackoverflow.com/questions/20699821/find-and-draw-regression-plane-to-a-set-of-points/20700063#20700063
# # @see: http://www.ilikebigbits.com/blog/2015/3/2/plane-from-points
# # @see: https://math.stackexchange.com/questions/99299/best-fitting-plane-given-a-set-of-points


# def bestfit_plane_numpy2(points):
#     from numpy import asarray
#     from numpy import sum
#     from numpy import hstack
#     from numpy import ones
#     from scipy.linalg import solve

#     xyz = asarray(points).reshape((-1, 3))
#     n = xyz.shape[0]
#     c = (sum(xyz, axis=0) / n).reshape((-1, 3))
#     A = hstack((xyz[:, 0:2], ones((xyz.shape[0], 1))))
#     b = xyz[:, 2:]
#     a, b, c = solve(A.T.dot(A), A.T.dot(b))
#     u = 1.0, 0.0, a[0]
#     v = 0.0, 1.0, b[0]
#     w = normalize_vector(cross_vectors(u, v))
#     return c, w


# def bestfit_plane_numpy3(points):
#     from numpy import asarray
#     from numpy import sum
#     from functools import partial
#     from scipy.optimize import minimize

#     def plane(x, y, abc):
#         a, b, c = abc
#         return a * x + b * y + c

#     def error(abc, points):
#         result = 0
#         for x, y, z in points:
#             znew = plane(x, y, abc)
#             result += (znew - z) ** 2
#         return result

#     c = sum(asarray(points), axis=0) / len(points)
#     objective = partial(error, points=points)
#     res = minimize(objective, [0, 0, 0])
#     a, b, c = res.x
#     u = 1.0, 0.0, a
#     v = 0.0, 1.0, b
#     w = normalize_vector(cross_vectors(u, v))
#     return c, w


# def bestfit_plane_numpy4(points):
#     from compas.numerical import pca_numpy

#     c, (_, _, w), _ = pca_numpy(points)
#     return c, w


def bestfit_circle_numpy(points):
    """Fit a circle through a set of points.

    Parameters
    ----------
    points : list
        XYZ coordinates of the points.

    Returns
    -------
    tuple
        XYZ coordinates of the center of the circle, the normal vector of the
        local frame, and the radius of the circle.

    Notes
    -----
    For more information see [1]_.

    References
    ----------
    .. [1] Scipy. *Least squares circle*.
           Available at: http://scipy-cookbook.readthedocs.io/items/Least_Squares_Circle.html.

    Examples
    --------
    .. code-block:: python

        #

    """
    o, uvw, _ = pca_numpy(points)
    rst = local_coords_numpy(o, uvw, points)
    x = rst[:, 0]
    y = rst[:, 1]

    def dist(xc, yc):
        return sqrt((x - xc) ** 2 + (y - yc) ** 2)

    def f(c):
        Ri = dist(*c)
        return Ri - Ri.mean()

    xm = mean(x)
    ym = mean(y)
    c0 = xm, ym
    c, ier = leastsq(f, c0)
    Ri = dist(*c)
    R = Ri.mean()
    residu = sum((Ri - R) ** 2)

    print(residu)

    xyz = global_coords_numpy(o, uvw, [[c[0], c[1], 0.0]])[0]

    o = xyz.tolist()
    u, v, w = uvw.tolist()

    return o, w, R


def bestfit_sphere_numpy(points):
    """Returns the sphere's center and radius that fits best through a set of points.

    Parameters
    ----------
    points: list of points
        XYZ coordinates of the points.

    Returns
    -------
    tuple: center, radius
        sphere center (XYZ coordinates) and sphere radius.

    Notes
    -----
    For more information see [1]_.

    References
    ----------
    .. [1] Least Squares Sphere Fit.
           Available at: https://jekel.me/2015/Least-Squares-Sphere-Fit/.

    Examples
    --------
    >>> from compas.geometry import bestfit_sphere_numpy
    >>> points = [(291.580, -199.041, 120.194), (293.003, -52.379, 33.599),\
                  (514.217, 26.345, 29.143), (683.253, 26.510, -6.194),\
                  (683.247, -327.154, 179.113), (231.606, -430.659, 115.458),\
                  (87.278, -419.178, -18.863), (24.731, -340.222, -127.158)]
    >>> center, radius = bestfit_sphere_numpy(points)
    """

    # Assemble the A matrix
    spX = asarray([p[0] for p in points])
    spY = asarray([p[1] for p in points])
    spZ = asarray([p[2] for p in points])
    A = zeros((len(spX), 4))
    A[:, 0] = spX*2
    A[:, 1] = spY*2
    A[:, 2] = spZ*2
    A[:, 3] = 1

    # Assemble the f matrix
    f = zeros((len(spX), 1))
    f[:, 0] = (spX*spX) + (spY*spY) + (spZ*spZ)
    C, residules, rank, singval = lstsq(A, f)

    # solve for the radius
    t = (C[0]*C[0]) + (C[1]*C[1]) + (C[2]*C[2]) + C[3]
    radius = sqrt(t)
    return [float(C[0][0]), float(C[1][0]), float(C[2][0])], radius


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    import doctest
    doctest.testmod()
