### $Id$
### $URL$

from geni.util.faults import *
from geni.util.misc import *
from geni.util.method import Method
from geni.util.parameter import Parameter, Mixed
from geni.util.auth import Auth
from geni.util.slices import Slices

class reset_slices(Method):
    """
    Reset the specified slice      

    @param cred credential string specifying the rights of the caller
    @param hrn human readable name of slice to instantiate
    @return 1 is successful, faults otherwise  
    """

    interfaces = ['aggregate', 'slicemgr']
    
    accepts = [
        Parameter(str, "Credential string"),
        Parameter(str, "Human readable name of slice to instantiate"),
        ]

    returns = [Parameter(int, "1 if successful")]
    
    def call(self, cred, hrn):
       
        self.api.auth.check(cred, 'resetslice')
        ## XX Not yet implemented
 
        return 1 
