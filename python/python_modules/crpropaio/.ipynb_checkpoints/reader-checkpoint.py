import numpy
import h5py
import astropy.cosmology
import astropy.coordinates as coord
import astropy.constants as const
import astropy.units as u


class LargeSphereEvents:
    def __init__(self, file_name, source_redshift, H0=70*u.km/u.s/u.Mpc, Om0=0.3):
        self.file_name = file_name
        self.source_redshift = source_redshift
        self.cosmology = astropy.cosmology.FlatLambdaCDM(H0=H0, Om0=Om0)
        
        self.source_distance = self.cosmology.comoving_distance(self.source_redshift)

        self.data = None
        self.arrival_position = None
        self.observed_direction = None
        self.time_delay = None
        
        self.read_events()
        self.compute_sky_coords()
        self.compute_time_delay()

    def read_events(self):
        with h5py.File(self.file_name, 'r') as input_stream:
            self.data = input_stream['CRPROPA3'][:]
        
        self.data['E'] *= 1e18
        
        for energy_container in ['E0', 'E1']:
            if energy_container in self.data.dtype.names:
                self.data[energy_container] *= 1e18

        self.data = self.data

    def compute_sky_coords(self):
        x = self.data['X'] - self.source_distance.to(u.Mpc).value
        y = self.data['Y'] - 0
        z = self.data['Z'] - 0
        r = (x**2 + y**2 + z**2)**0.5

        # Rotation angles wrt every particle's arrival point
        theta_rot = -numpy.arcsin(z / r)
        phi_rot   = +numpy.arctan2(y, x)

        # Computing direction angles from the observer's point of view
        # Rotation over the Z axis
        _x = numpy.cos(-phi_rot)*self.data['Px'] - numpy.sin(-phi_rot)*self.data['Py'] + 0*self.data['Pz']
        _y = numpy.sin(-phi_rot)*self.data['Px'] + numpy.cos(-phi_rot)*self.data['Py'] + 0*self.data['Pz']
        _z =                   0*self.data['Px'] +                   0*self.data['Py'] + 1*self.data['Pz']
        # Rotation over the Y axis
        px_obs =  numpy.cos(-theta_rot)*_x + 0*_y + numpy.sin(-theta_rot)*_z
        py_obs =                      0*_x + 1*_y +                     0*_z
        pz_obs = -numpy.sin(-theta_rot)*_x + 0*_y + numpy.cos(-theta_rot)*_z

        theta_obs = -numpy.arcsin(pz_obs / 1)
        phi_obs   = -numpy.arctan2(py_obs, px_obs)

        self.arrival_position = coord.SkyCoord(phi_rot, theta_rot, unit='rad')
        self.observed_direction = coord.SkyCoord(phi_obs, theta_obs, unit='rad')

    def compute_time_delay(self):
        primary_photons = (self.data['ID1'] == 22) & (self.data['ID'] == 22)
        ref_dist = self.data['D'][primary_photons].mean()

        path_diff = (self.data['D'] - ref_dist) * u.Mpc
        tdelay = (path_diff / const.c).decompose()
        tdelay = tdelay.to(u.yr)

        self.time_delay = tdelay
