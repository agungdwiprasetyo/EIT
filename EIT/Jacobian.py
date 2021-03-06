from __future__ import division, absolute_import, print_function

import numpy as np
import scipy.linalg as la
from EIT.PDE import pdeprtni
from .EITbase import EITBase

class Jacobian(EITBase):
    """ implementing a JAC class """

    def setup(self, p=0.20, lamb=0.001, method='kotre'):
        """
        JAC, default file parser is 'std'

        Parameters
        ----------
        p, lamb : float
            JAC parameters
        method : str
            regularization methods
        """
        # pre-compute H0 for dynamical imaging
        # H = (J.T*J + R)^(-1) * J.T
        self.H = h_matrix(self.jacobian, p, lamb, method) # H = solusi
        self.params = {
            'p': p,
            'lamb': lamb,
            'method': method
        }

    def solve(self, v1, v0, normalize=False):
        """ dynamic solve

        Parameters
        ----------
        v1 : NDArray
        v0 : NDArray, optional
            d = H(v1 - v0)
        normalize : Boolean
            true for conducting normalization

        Returns
        -------
        NDArray
            complex-valued NDArray, changes of conductivities
        """
        # normalize usually is not required for JAC
        if normalize:
            dv = - (v1 - v0) / v0
        else:
            dv = (v1 - v0)
        # s = -Hv
        ds = - np.dot(self.H, dv)
        # return average epsilon on element

        hasil = pdeprtni(self.node, self.element, ds)
        return hasil

    def map(self, v):
        """ return Hv """
        return -np.dot(self.H, v)

    def solveGramSchmidt(self, v1, v0):
        """ solving by weighted frequency / Gram-Schmidt"""
        a = np.dot(v1, v0) / np.dot(v0, v0)
        dv = (v1 - a*v0)    # (v1 - a*v0)/np.sign(v0)
        ds = -np.dot(self.H, dv)
        # return average epsilon on element
        return np.real(ds)

    def bp_solve(self, v1, v0, normalize=False):
        """ solve via a 'naive' back projection. """
        # normalize usually is not required for JAC
        if normalize:
            dv = - (v1 - v0)/v0
        else:
            dv = (v1 - v0)
        # s_r = J^Tv_r
        ds = - np.dot(self.jacobian.T.conjugate(), dv)
        # return average epsilon on element
        return ds

    def gn(self, v, x0=None, maxiter=1, gtol=1e-4, p=None, lamb=None,
           lamb_decay=1.0, lamb_min=0, method='kotre', verbose=False):
        """
        Gaussian Newton Static Solver
        You can use a different p, lamb other than the default ones in setup

        Parameters
        ----------
        v : NDArray
            boundary measurement
        x0 : NDArray, optional
            initial guess
        maxiter : int, optional
        p, lamb : float
            JAC parameters (can be overridden)
        lamb_decay : float
            decay of lamb0, i.e., lamb0 = lamb0 * lamb_delay of each iteration
        lamb_min : float
            minimal value of lamb
        method : str, optional
            'kotre' or 'lm'
        verbose : bool, optional
            print debug information

        Returns
        -------
        NDArray
            Complex-valued conductivities

        Note
        ----
        Gauss-Newton Iterative solver,
            x1 = x0 - (J^TJ + lamb*R)^(-1) * r0
        where:
            R = diag(J^TJ)**p
            r0 (residual) = real_measure - forward_v
        """
        if x0 is None:
            x0 = self.perm
        if p is None:
            p = self.params['p']
        if lamb is None:
            lamb = self.params['lamb']
        if method is None:
            method = self.params['method']

        # convergence test
        x0_norm = np.linalg.norm(x0)

        for i in range(maxiter):

            # forward solver
            fs = self.fwd.solve(self.ex_mat, step=self.step,
                                perm=x0, parser=self.parser)
            # Residual
            r0 = v - fs.v
            jac = fs.jac

            # Damped Gaussian-Newton
            h_mat = h_matrix(jac, p, lamb, method)

            # update
            d_k = np.dot(h_mat, r0)
            x0 = x0 - d_k

            # convergence test
            c = np.linalg.norm(d_k) / x0_norm

            # update regularization parameter
            # TODO: support user defined decreasing order of lambda values
            if lamb > lamb_min:
                lamb *= lamb_decay

            if c < gtol:
                break

            if verbose:
                print('iter = %d, lamb = %f, gtol = %f' % (i, lamb, c))

        return x0

    def project(self, ds):
        """ project ds using spatial difference filter (deprecated)

        Parameters
        ----------
        ds : NDArray
            delta sigma (conductivities)

        Returns
        -------
        NDArray
        """
        d_mat = sar(self.element)
        return np.dot(d_mat, ds)


def h_matrix(jac, p, lamb, method='kotre'):
    """
    JAC method of dynamic EIT solver:
        H = (J.T*J + lamb*R)^(-1) * J.T

    Parameters
    ----------
    jac : NDArray
        Jacobian
    p, lamb : float
        regularization parameters
    method : str, optional
        regularization method

    Returns
    -------
    NDArray
        pseudo-inverse matrix of JAC
    """
    j_w_j = np.dot(jac.transpose(), jac)
    if method is 'kotre':
        # see adler-dai-lionheart-2007, 'kotr' for short
        # p=0   : noise distribute on the boundary ('lm')
        # p=0.5 : noise distribute on the middle
        # p=1   : noise distribute on the center
        r_mat = np.diag(np.diag(j_w_j) ** p)
    elif method is 'lm':
        # Marquardt–Levenberg, 'lm' for short
        r_mat = np.diag(np.diag(j_w_j))
    else:
        # Damped Gauss Newton, 'dgn' for short
        r_mat = np.eye(jac.shape[1])

    # build H
    h_mat = np.dot(la.inv(j_w_j + lamb*r_mat), jac.transpose())
    return h_mat


def sar(el2no):
    """
    extract spatial difference matrix on the neighbors of each element
    in 2D fem using triangular mesh.

    Parameters
    ----------
    el2no : NDArray
        triangle structures

    Returns
    -------
    NDArray
        SAR matrix
    """
    ne = el2no.shape[0]
    d_mat = np.eye(ne)
    for i in range(ne):
        ei = el2no[i, :]
        #
        i0 = np.argwhere(el2no == ei[0])[:, 0]
        i1 = np.argwhere(el2no == ei[1])[:, 0]
        i2 = np.argwhere(el2no == ei[2])[:, 0]
        idx = np.unique(np.hstack([i0, i1, i2]))
        # build row-i
        for j in idx:
            d_mat[i, j] = -1
        nn = idx.size - 1
        d_mat[i, i] = nn
    return d_mat