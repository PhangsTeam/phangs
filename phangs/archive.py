import numpy as np
import warnings

try:
    import paramiko
    have_ssh = True
except ModuleNotFoundError:
    # warnings.warn("paramiko module not found.  SSH access to Archive diabled")
    have_ssh = False
        

__all__ = ['retrieve']

def retrieve(galaxy=['all'],
             product=['mom0'],
             exclude=[None],
             method='ssh'):
    
    pass
