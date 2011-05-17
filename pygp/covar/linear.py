"""
Classes for linear covariance function
======================================
Linear covariance functions

LinearCFISO
LinearCFARD

"""

#TODO: fix ARD covariance 

import scipy as SP
from pygp.covar import CovarianceFunction


class LinearCFISO(CovarianceFunction):
    """
    isotropic linear covariance function with a single hyperparameter
    """

    def __init__(self,*args,**kw_args):
        super(LinearCFISO, self).__init__(*args,**kw_args)
        self.n_hyperparameters = 1

    def K(self,theta,x1,x2=None):
        #get input data:
        x1, x2 = self._filter_input_dimensions(x1,x2)
        # 2. exponentiate params:
        A  = SP.exp(2*theta[0])
        RV = A*SP.dot(x1,x2.T)
        return RV

    def Kdiag(self,theta,x1,i):
        x1 = self._filter_x(x1)
        RV = SP.dot(x1,x1).sum(axis=1)
        RV*=2
        return RV


    def Kgrad_theta(self,theta,x1,i):
        RV = self.K(theta,x1)
        #derivative w.r.t. to amplitude
        RV*=2
        return RV


    def Kgrad_x(self,theta,x1,x2,d):
        A = SP.exp(2*theta[0])
        RV = SP.zeros([x1.shape[0],x2.shape[0]])
        if d not in self.dimension_indices:
            return RV
        RV[:,:] = A*x2[:,d]
        return RV

    
    def Kgrad_xdiag(self,theta,x1,d):
        """derivative w.r.t diagonal of self covariance matrix"""
        A = SP.exp(2*theta[0])
        RV = SP.zeros([x1.shape[0]])
        if d not in self.dimension_indices:
            return RV
        RV[:] = 2*A*x1[:,d]
        return RV



class LinearCFARD(CovarianceFunction):
    """identical to LinearCF, however alternative paramerterisation of the ard parameters"""

    def __init__(self,n_dimensions=1,dimension_indices=None):
        if dimension_indices != None:
            self.dimension_indices = SP.array(dimension_indices,dtype='int32')
        elif n_dimensions:
            self.dimension_indices = SP.arange(0,n_dimensions)
        if (len(self.dimension_indices)>0):
            self.n_dimensions = len(self.dimension_indices)
            self.n_hyperparameters = self.n_dimensions
        else:
            self.n_dimensions = 0
            self.n_hyperparameters = 0
        
       
    def get_hyperparameter_names(self):
        names = []
        names.append('Amplitude')
        return names

    def K(self,theta,x1,x2=None):
        if x2 is None:
            x2 = x1
        # 2. exponentiate params:
        #L  = SP.exp(-2*theta[0:self.n_dimensions])
        L  = 1./theta[0:self.n_dimensions]
        RV = SP.zeros([x1.shape[0],x2.shape[0]])
        for i in xrange(self.n_dimensions):
            iid = self.dimension_indices[i]
            RV+=L[i]*SP.dot(x1[:,iid:iid+1],x2[:,iid:iid+1].T)
        return RV

    def Kgrad_theta(self,theta,x1,i):
        iid = self.dimension_indices[i]
        #Li = SP.exp(-2*theta[i])
        Li = 1./theta[i]
        RV = -1*Li**2*SP.dot(x1[:,iid:iid+1],x1[:,iid:iid+1].T)
        return RV
    

    def Kgrad_x(self,theta,x1,x2,d):
        RV = SP.zeros([x1.shape[0],x2.shape[0]])
        if d not in self.dimension_indices:
            return RV
        #get corresponding amplitude:
        i = SP.nonzero(self.dimension_indices==d)[0][0]
        #A = SP.exp(-2*theta[i])
        A = 1./theta[i]
        RV[:,:] = A*x2[:,d]
        return RV

    
    def Kgrad_xdiag(self,theta,x1,d):
        """derivative w.r.t diagonal of self covariance matrix"""
        RV = SP.zeros([x1.shape[0]])
        if d not in self.dimension_indices:
            return RV
        #get corresponding amplitude:
        i = SP.nonzero(self.dimension_indices==d)[0][0]
        #A = SP.exp(-2*theta[i])
        A = 1./theta[i]
        RV = SP.zeros([x1.shape[0]])
        RV[:] = 2*A*x1[:,d]
        return RV
