from astropy.coordinates import SkyCoord, Angle, FK5
from astroquery.ned import Ned
import astropy.units as u
from astropy.table import Table
from astropy.io import fits
from astropy.wcs import WCS
import warnings
import numpy as np
from astropy.utils.data import get_pkg_data_filename
import os
import glob

def parse_galtable(galobj, name):
    # TODO: Generalize
    if os.environ('PHANGSDATA') is not None:
        table_dir = os.environ('PHANGSDATA') + '/Archive/Products/sample_tables/'
        fl = glob.glob(table_dir + '*.fits')
        # TODO: This isn't right
        table_name = fl[-1]
    else:
    table   _name = get_pkg_data_filename('data/phangs_sample_table_v1p4.fits',
                                           package='phangs')
    galtable = Table.read(table_name)
    hits = [x for x in galtable if name in x['ALIAS']]
    if len(hits) > 0:
        if len(hits) > 1:
            exact = np.zeros(len(hits), dtype=np.bool)
            for i, h in enumerate(hits):
                exact[i] = np.any(
                    [n.strip() == name for n in h['ALIAS'].split(';')])
            if np.sum(exact) == 1:
                thisobj = hits[(np.where(exact))[0][0]]
            else:
                raise Exception("More than one exact match in galbase")
        else:
            thisobj = hits[0]
        galobj.name = thisobj['NAME'].strip()
        galobj.vsys = thisobj['VRAD_KMS'] * u.km / u.s
        galobj.center_position = SkyCoord(
            thisobj['RA_DEG'], thisobj['DEC_DEG'], frame='fk5',
            unit='degree')
        galobj.distance = thisobj['DIST_MPC'] * u.Mpc
        galobj.inclination = thisobj['INCL_DEG'] * u.deg
        galobj.position_angle = thisobj['POSANG_DEG'] * u.deg
        galobj.provenance = 'GalBase'
        return True

class PhangsGalaxy(object):
    '''
    Parameters
    ----------
    name : str
        Name of the galaxy.the
    params : dict, optional
        Optionally provide custom parameter values as a dictionary.
    '''

    def __init__(self, name, params=None):

        self.name = name
# An astropy coordinates structure
        self.center_position = None
# This is the preferred name in a database.
        self.canonical_name = None
# With units
        self.distance = None
        self.inclination = None
        self.position_angle = None
        self.redshift = None
        self.vsys = None
        self.PA_is_kinematic = False
        self.provenance = None
