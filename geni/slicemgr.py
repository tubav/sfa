### $Id$
### $URL$

import os
import sys
import datetime
import time

from geni.util.geniserver import *
from geni.util.geniclient import *
from geni.util.faults import *
from geni.util.misc import *

class SliceMgr(GeniServer):

  
    ##
    # Create a new slice manager object.
    #
    # @param ip the ip address to listen on
    # @param port the port to listen on
    # @param key_file private key filename of registry
    # @param cert_file certificate filename containing public key (could be a GID file)     

    def __init__(self, ip, port, key_file, cert_file, config = "/usr/share/geniwrapper/geni/util/geni_config"):
        GeniServer.__init__(self, ip, port, key_file, cert_file)
        self.server.interface = 'slicemgr'      
