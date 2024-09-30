import numpy
import astropy.units as u

from .observer import EventContainer, EventData


def power_law(e, e0, norm, index):
    return norm * (e/e0)**index


def power_law_ecut(e, e0, norm, index, ecut):
    return norm * (e/e0)**index * numpy.exp(-(e/ecut))


class SimpleLightCurve:
    def __init__(self, observer, ref_mjd_edges, ref_energy_range):
        """
        Parameters
        ----------
        observer: crpropaio.observer.Observer
            Observer instance holding the recorded events data
        ref_mjd_edges: ndarray
            Reference MJD dates
        ref_energy_range: list
            Lower/upper edges of the energy range the reference flux corresponds to
        """
        
        self.observer = observer
        
        self.__ref_mjd_edges = ref_mjd_edges
        self.__ref_energy_range = ref_energy_range

    @property
    def ref_mjd_edges(self):
        return self.__ref_mjd_edges
    
    @property
    def ref_energy_range(self):
        return self.__ref_energy_range

    def predict_lc(self, ref_flux, energy_range, mjd_edges=None, kind='primary'):
        """
        Computes the primary source flux light curve.
        
        Parameters
        ----------
        ref_flux: ndarray
            Flux to assume on the reference dates.
        energy_range: list
            Lower/upper edges of the energy range for which to evaluate the light curve.
        mjd_edges: ndarray, optional
            MJD edges of the time intervals, for which to evaluate the light curve.
        kind: str
            Light curve kind, one of 'primary' or 'secondary'
        """
        
        if kind not in ['primary', 'secondary']:
            raise ValueError(f'Unsupported light curve kind "{kind}"')
        
        if mjd_edges is None:
            mjd_edges = numpy.linspace(self.ref_mjd_edges.min(), self.ref_mjd_edges.max(), num=30)

        ref_primary_selection = (self.observer.events.primary.energy >= self.ref_energy_range[0]) & (self.observer.events.primary.energy < self.ref_energy_range[1])
        nprimary = sum(ref_primary_selection)

        tdelay = u.Quantity(numpy.zeros((0,)), unit=u.yr)
        weights = numpy.zeros((0,))

        if kind == 'primary':
            selection = (self.observer.events.primary.energy >= energy_range[0]) & (self.observer.events.primary.energy < energy_range[1])
            evt_tdelay =  self.observer.events.primary.time_delay[selection]
        else:
            selection = (self.observer.events.secondary.energy >= energy_range[0]) & (self.observer.events.secondary.energy < energy_range[1])
            evt_tdelay =  self.observer.events.secondary.time_delay[selection]
        
        for tstart, tstop, flux in zip(self.ref_mjd_edges[:-1], self.ref_mjd_edges[1:], ref_flux):
            dt = tstop - tstart
            tmean = (tstop + tstart) / 2
            
            expected_primary = flux * dt
            flux_norm = expected_primary / nprimary
            
            tdelay = numpy.concatenate((tdelay, evt_tdelay + tmean * u.day))
            weights = numpy.concatenate((weights, flux_norm * numpy.ones_like(evt_tdelay.value)))
            
        flux, mjd_edges = numpy.histogram(
            tdelay.to(u.day).value,
            weights=weights,
            bins=mjd_edges,
        )

        flux /= numpy.diff(mjd_edges)

        lc = {
            'flux': flux,
            'mjd_edges': mjd_edges,
            'mjd': (mjd_edges[1:] + mjd_edges[:-1]) / 2,
            'mjd_err': (mjd_edges[1:] - mjd_edges[:-1]) / 2,
        }
        
        return lc


class SpectrumEvolutionModel:
    def __init__(self, observer, sim_spec):
        self.observer = observer
            
        primaries_detected = observer.events.primary.energy
        primaries_absorbed = numpy.unique(observer.events.secondary.parent_energy)
        
        #primaries = numpy.concatenate((primaries_detected, primaries_absorbed))
        #n_primaries = len(primaries)
        
        #emin = primaries.min()
        #emax = primaries.max()
        #e0 = (emin * emax)**0.5
        
        #if sim_index == -1:
            #norm = n_primaries / e0 / (numpy.log(emax/e0) - numpy.log(emin/e0))
        #else:
            #norm = n_primaries * (sim_index + 1) / e0 / ((emax/e0)**((sim_index + 1)) - (emin/e0)**((sim_index + 1)))
        
        #norm *= observer.beam_fraction
        
        #self.index = sim_index
        #self.norm = norm
        #self.e0 = e0
        
        self.sim_spec = sim_spec

    def primary_sed(self, energy_edges, norm, e0, index, ecut, intrinsic=False):
        #norm = norm / e0**2
        
        if intrinsic:
            primaries_detected = self.observer.events.primary.energy
            primaries_absorbed = numpy.unique(self.observer.events.secondary.parent_energy)
            energy = numpy.concatenate((primaries_detected, primaries_absorbed))
        else:
            energy = self.observer.events.primary.energy
        
        expected_flux = power_law_ecut(energy, e0, norm, index, ecut)
        model_flux = power_law(energy, self.sim_spec['e0'], self.sim_spec['norm'], self.sim_spec['index'])
               
        weights = (expected_flux / model_flux).decompose()
       # weights /= self.observer.area
        weights *= energy
        
        e2dnde, edges = numpy.histogram(
            energy,
            weights=weights,
            bins=energy_edges
        )
        
        dloge = numpy.diff(numpy.log(edges/e0))
        e2dnde /= dloge
        
        return e2dnde
        
    def secondary_sed(self, energy_edges, norm, e0, index, ecut, tmin=None, tmax=None):
        if tmin is None:
            tmin = self.observer.events.secondary.time_delay.min()
            
        if tmax is None:
            tmax = self.observer.events.secondary.time_delay.max()
        
        #norm = norm / e0**2
        
        energy = self.observer.events.secondary.energy
        parent_energy = self.observer.events.secondary.parent_energy
        
        expected_flux = power_law_ecut(parent_energy, e0, norm, index, ecut)
        model_flux = power_law(parent_energy, self.sim_spec['e0'], self.sim_spec['norm'], self.sim_spec['index'])
               
        weights = (expected_flux / model_flux).decompose()
        # weights /= self.observer.area
        weights *= energy
        
        selection = (self.observer.events.secondary.time_delay >= tmin) & (self.observer.events.secondary.time_delay < tmax)
        
        e2dnde, edges = numpy.histogram(
            energy[selection],
            weights=weights[selection],
            bins=energy_edges
        )
        
        dloge = numpy.diff(numpy.log(edges/e0))
        e2dnde /= dloge
        
        return e2dnde
        

    

