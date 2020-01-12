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

__all__ = ['PhangsGalaxy']

def _parse_galtable(galobj, name):
    # TODO: Generalize
    if os.environ.get('PHANGSDATA') is not None:
        table_dir = os.environ.get('PHANGSDATA') + '/Archive/Products/sample_tables/'
        fl = glob.glob(table_dir + '*.fits')
        # TODO: This isn't right
        table_name = fl[-1]
    else:
        table_name = get_pkg_data_filename('data/phangs_sample_table_v1p4.fits',
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
        galobj.vsys = thisobj['ORIENT_VLSR'] * u.km / u.s
        galobj.center_position = SkyCoord(
            thisobj['ORIENT_RA'], thisobj['ORIENT_DEC'], frame='fk5',
            unit='degree')
        galobj.distance = thisobj['DIST'] * u.Mpc
        galobj.inclination = thisobj['ORIENT_INCL'] * u.deg
        galobj.position_angle = thisobj['ORIENT_POSANG'] * u.deg
        galobj.PA_is_kinematic = True
        galobj.provenance = 'PhangsTable'
        galobj.has_alma = bool(thisobj['HAS_ALMA'])
        galobj.has_astrosat = bool(thisobj['HAS_ASTROSAT'])
        galobj.has_dense = bool(thisobj['HAS_DENSE'])
        galobj.has_muse = bool(thisobj['HAS_MUSE'])
        galobj.has_galex = bool(thisobj['HAS_GALEX'])
        galobj.has_halpha = bool(thisobj['HAS_HALPHA'])
        galobj.has_herschel = bool(thisobj['HAS_HERSCHEL'])
        galobj.has_hi = bool(thisobj['HAS_HI'])
        galobj.has_hst = bool(thisobj['HAS_HST'])
        galobj.has_irac = bool(thisobj['HAS_IRAC'])
        galobj.has_muse = bool(thisobj['HAS_MUSE'])
        galobj.mw_av = thisobj['MWAV_SF11'] * u.mag
        galobj.morph_T = thisobj['MORPH_T']
        galobj.morph_bar = bool(thisobj['MORPH_BAR'])
        galobj.m_star = 1e1 ** (thisobj['MSTAR_LOGMSTAR']) * u.M_sun
        galobj.m_hi = 1e1 ** (thisobj['HI_LOGMHI']) * u.M_sun
        galobj.m_h2 = 1e1 ** (thisobj['CO_LOGMH2']) * u.M_sun
        galobj.r25 = thisobj['SIZE_OPT_R25'] * u.arcsec
        
        
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
        
        if params is not None:
            if not isinstance(params, dict):
                raise TypeError("params must be a dictionary.")

            required_params = ["center_position", "distance", "inclination",
                               "position_angle", "vsys"]
            optional_params = ["canonical_name", "redshift"]

            keys = params.keys()
            for par in required_params:
                if par not in keys:
                    raise ValueError("params is missing the required key"
                                     " {}".format(par))
                setattr(self, par, params[par])

            for par in optional_params:
                if par in keys:
                    setattr(self, par, params[par])
        else:
            if not _parse_galtable(self, name):
                try:
                    t = Ned.query_object(name)
                    if len(t) == 1:
                        self.canonical_name = t['Object Name'][0]
                        self.velocity = t['Velocity'][0] * u.km / u.s
                        self.center_position = \
                            SkyCoord(t['RA(deg)'][0], t['DEC(deg)'][0],
                                     frame='fk5',
                                     unit='degree')
                        self.redshift = t['Redshift'][0]
                        self.provenance = 'NED'
                except:
                    warnings.warn("Unsuccessful query to NED")
                    pass

    def __repr__(self):
        return "Galaxy {0} at RA={1}, DEC={2}".format(self.name,
                                                      self.center_position.ra,
                                                      self.center_position.dec)

    def skycoord_grid(self, header=None, wcs=None):
        '''
        Return a grid of RA and Dec values.
        '''
        if header is not None:
            w = WCS(header)
        elif wcs is not None:
            w = wcs
        else:
            raise ValueError("header or wcs must be given.")
        w = WCS(header)
        ymat, xmat = np.indices((w.celestial._naxis2, w.celestial._naxis1))
        ramat, decmat = w.celestial.wcs_pix2world(xmat, ymat, 0)
        return SkyCoord(ramat, decmat, unit=(u.deg, u.deg))

    def radius(self, skycoord=None, ra=None, dec=None,
               header=None, returnXY=False):
        if skycoord:
            PAs = self.center_position.position_angle(skycoord)
            Offsets = skycoord
        elif isinstance(header, fits.Header):
            Offsets = self.skycoord_grid(header=header)
            PAs = self.center_position.position_angle(Offsets)
        elif np.any(ra) and np.any(dec):
            Offsets = SkyCoord(ra, dec, unit=(u.deg, u.deg))
            PAs = self.center_position.position_angle(Offsets)
        else:
            warnings.warn('You must specify either RA/DEC, a header or a '
                          'skycoord')
        GalPA = PAs - self.position_angle
        GCDist = Offsets.separation(self.center_position)
        # Transform into galaxy plane
        Rplane = self.distance * np.tan(GCDist)
        Xplane = Rplane * np.cos(GalPA)
        Yplane = Rplane * np.sin(GalPA)
        Xgal = Xplane
        Ygal = Yplane / np.cos(self.inclination)
        Rgal = np.sqrt(Xgal**2 + Ygal**2)
        if returnXY:
            return (Xgal.to(u.pc), Ygal.to(u.pc))
        else:
            return Rgal.to(u.pc)

    def position_angles(self, skycoord=None, ra=None, dec=None,
                        header=None):
        X, Y = self.radius(skycoord=skycoord, ra=ra, dec=dec,
                           header=header, returnXY=True)

        return Angle(np.arctan2(Y, X))

    def to_center_position_pixel(self, wcs=None, header=None):

        if header is not None:
            wcs = WCS(header)

        if wcs is None:
            raise ValueError("Either wcs or header must be given.")

        return self.center_position.to_pixel(wcs)

    def rotation_curve(self):
        # Gonna be great!
        raise NotImplementedError
        pass
