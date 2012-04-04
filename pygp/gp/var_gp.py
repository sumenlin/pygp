'''
Created on 2 Apr 2012

@author: maxz
'''
from pygp.gp.gp_base import GP
import scipy
from scipy import linalg
from scipy.lib.lapack import flapack
from pygp.linalg.linalg_matrix import jitChol

class VarGP(GP):
    '''
    Class for variational GP.
    '''

    def __init__(self, n_inducing_variables, **kwargs):
        self.m = n_inducing_variables
        self.jitter = 1E-6
        super(VarGP, self).__init__(**kwargs)
    
    def LML(self, hyperparams, priors=None, **kw_args):
        #LML = super(VarGP, self).LML(hyperparams, priors=priors, **kw_args)
        
        LML = self._LML_Xm(hyperparams)
        return LML
    
    def LMLgrad(self, hyperparams, priors=None, **kw_args):
#        pdb.set_trace()
        """
        Returns the log Marginal likelihood for the given logtheta.

        **Parameters:**

        hyperparams : {'covar':CF_hyperparameters, ...}
            The hyperparameters which shall be optimized and derived

        priors : [:py:class:`lnpriors`]
            The hyperparameters which shall be optimized and derived

        """
        
        RV = self._LMLgrad_covar(hyperparams)
        if self.likelihood is not None:
            RV.update(self._LMLgrad_lik(hyperparams))

        #gradients w.r.t x:
        RV_ = self._LMLgrad_Xm(hyperparams)
        #update RV
        RV.update(RV_)

        #prior
        if priors is not None:
            plml = self._LML_prior(hyperparams, priors=priors, **kw_args)
            for key in RV.keys():
                RV[key] -= plml[key][:, 1]
        return RV

    def _LML_Xm(self, hyperparams):
        if 'Xm' not in hyperparams.keys():
            return {}
        Q = self._compute_sparsified_covariance(hyperparams)
        
        # get correction term:
        correction_term = (1./(2.*scipy.power(self.jitter,2))) * scipy.sum(self.covar.Kdiag(hyperparams['covar'], self._get_x()) - scipy.diag(Q, 0))
        
        # add jitter
        n = self._get_x().shape[0]
        jit_mat = scipy.zeros((n,n))
        scipy.fill_diagonal(jit_mat, self.jitter)
        Q += jit_mat
        
        y = self._get_y()

        import pdb;pdb.set_trace()
        
        rv  = -y.shape[0]*scipy.log(2*scipy.pi)
        
        
        #rv -= scipy.log(linalg.det(Q)) # >>>>>> allways zero <<<<< ????
        
        rv -= scipy.dot(y.T, linalg.solve(Q, y))
        
        return .5*rv - correction_term

    def _LMLgrad_Xm(self, hyperparams):
        if 'Xm' not in hyperparams.keys():
            return {}
        return {}

    def _compute_sparsified_covariance(self, hyperparams):
        Xm = hyperparams['Xm']
        # sparse computation of covariance Q:       
        cross_covariance = self.covar.K(hyperparams['covar'], self._get_x(), Xm) # Knm
        sparse_covariance = self.covar.K(hyperparams['covar'], Xm) # Kmm
        # cholesky lower triangular matrix
        L = jitChol(sparse_covariance)
        # invert by dpotri
        
        Linv = flapack.dpotri(L)[0]
        A = scipy.dot(cross_covariance, Linv)
        Q1 = scipy.dot(A,A.T)
        Q2 = scipy.dot(cross_covariance, linalg.solve(sparse_covariance, cross_covariance.T))
        import pdb;pdb.set_trace()
        #             Knm        dot           Kmm^-1 dot Kmn
        return Q1
    

        
        
        