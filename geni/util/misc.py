from excep import *

def get_leaf(hrn):
    parts = hrn.split(".")
    return ".".join(parts[-1:])

def get_authority(hrn):
    
    parts = hrn.split(".")
    return ".".join(parts[:-1])

def get_auth_type(type):
    if (type=="slice") or (type=="user") or (type=="sa"):
        return "sa"
    elif (type=="component") or (type=="ma"):
        return "ma"
    else:
        raise UnknownGeniType(type)

def hrn_to_pl_slicename(hrn):
    parts = hrn.split(".")
    return parts[-2] + "_" + parts[-1]

# assuming hrn is the hrn of an authority, return the plc authority name
def hrn_to_pl_authname(hrn):
    parts = hrn.split(".")
    return parts[-1]

# assuming hrn is the hrn of an authority, return the plc login_base
def hrn_to_pl_login_base(hrn):
    return hrn_to_pl_authname(hrn)

def hostname_to_hrn(self, login_base, hostname):
    """
    Convert hrn to plantelab name.
    """
    genihostname = "_".join(hostname.split("."))
    return ".".join([self.hrn, login_base, genihostname])

def slicename_to_hrn(self, slicename):
    """
    Convert hrn to planetlab name.
    """
    parts = slicename.split("_")
    slice_hrn = ".".join([self.hrn, parts[0]]) + "." + "_".join(parts[1:])

    return slice_hrn

