from spectral_cube import SpectralCube, Projection
import os
import astropy.units as u

__all__ = ['convolve_to_resolution']

def convolve_to_resolution(filenames, resolution=100 * u.pc, sample_table=None, **kwargs):
    """
    Convolves an FITS image to a given linear resolution from a given distance sample table
    """    
    
    if type(filenames) is list:
        for filename in filenames:
            convolve_to_resolution(filename, resolution=resolution, **kwargs)
            return()        
    
    print(filenames)