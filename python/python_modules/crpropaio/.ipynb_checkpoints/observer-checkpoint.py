import numpy
import astropy.units as u
import astropy.coordinates as coord


class EventContainer:
    def __init__(self, primary, secondary):
        self.__primary = primary
        self.__secondary = secondary

    @property
    def primary(self):
        return self.__primary

    @property
    def secondary(self):
        return self.__secondary


class EventData:
    def __init__(self, energy, direction, time_delay, parent_energy=None):
        self.__energy = energy
        self.__direction = direction
        self.__time_delay = time_delay
        self.__parent_energy = parent_energy

    @property
    def energy(self):
        return self.__energy

    @property
    def direction(self):
        return self.__direction

    @property
    def time_delay(self):
        return self.__time_delay
    
    @property
    def parent_energy(self):
        return self.__parent_energy


class Observer:
    def __init__(self, events, sky_pos, max_pos_offset, max_obs_offset=180*u.deg):
        self.sky_pos = sky_pos
        self.max_pos_offset = max_pos_offset
        self.max_obs_offset = max_obs_offset

        pos_offset = self.sky_pos.separation(events.arrival_position)

        zero_point = coord.SkyCoord(0, 0, unit='deg')
        obs_offset = zero_point.separation(events.observed_direction)

        primary_filter = (events.data['ID1'] == 22) & (events.data['ID'] == 22)
        secondary_filter = (events.data['ID1'] != 22) & (events.data['ID'] == 22)

        primary = primary_filter & (pos_offset < max_pos_offset) & (obs_offset < max_obs_offset)
        secondary = secondary_filter & (pos_offset < max_pos_offset) & (obs_offset < max_obs_offset)

        primary_events = EventData(
            energy=events.data['E'][primary] * u.eV,
            direction=events.observed_direction[primary],
            time_delay=events.time_delay[primary]
        )
        
        if 'E0' in events.data.dtype.names:
            secondary_events = EventData(
                energy=events.data['E'][secondary] * u.eV,
                direction=events.observed_direction[secondary],
                time_delay=events.time_delay[secondary],
                parent_energy=events.data['E0'][secondary] * u.eV
            )
        else:
            secondary_events = EventData(
                energy=events.data['E'][secondary] * u.eV,
                direction=events.observed_direction[secondary],
                time_delay=events.time_delay[secondary],
                parent_energy=None
            )

        self.events = EventContainer(primary_events, secondary_events)

    def primary_lc(self, ref_mjd, ref_flux, ref_energy_range, energy_range, mjd_edges=None):
        if mjd_edges is None:
            mjd_edges = numpy.linspace(ref_mjd.min(), ref_mjd.max(), num=30)

        ref_primary_selection = (self.events.primary.energy >= ref_energy_range[0]) & (self.events.primary.energy < ref_energy_range[1])
        nprimary = sum(ref_primary_selection)

        dmjd = numpy.diff(ref_mjd).mean()

        tdelay = u.Quantity(numpy.zeros((0,)), unit=u.yr)
        weights = numpy.zeros((0,))

        selection = (self.events.primary.energy >= energy_range[0]) & (self.events.primary.energy < energy_range[1])
        orig_tdelay =  self.events.primary.time_delay[selection]
        
        for mjd, flux in zip(ref_mjd, ref_flux):
            tdelay = numpy.concatenate((tdelay, orig_tdelay + mjd*u.day))
            expected_primary = flux * dmjd
            flux_norm = expected_primary / nprimary
            weights = numpy.concatenate((weights, flux_norm*numpy.ones_like(orig_tdelay.value)))
            
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

    def secondary_lc(self, ref_mjd, ref_flux, ref_energy_range, energy_range, mjd_edges=None):
        if mjd_edges is None:
            mjd_edges = numpy.linspace(ref_mjd.min(), ref_mjd.max(), num=30)

        primary_selection = (self.events.primary.energy >= ref_energy_range[0]) & (self.events.primary.energy < ref_energy_range[1])
        nprimary = sum(primary_selection)

        dmjd = numpy.diff(ref_mjd).mean()

        tdelay = u.Quantity(numpy.zeros((0,)), unit=u.yr)
        weights = numpy.zeros((0,))

        secondary_selection = (self.events.secondary.energy >= energy_range[0]) & (self.events.secondary.energy < energy_range[1])
        orig_tdelay =  self.events.secondary.time_delay[secondary_selection]
        
        for mjd, flux in zip(ref_mjd, ref_flux):
            tdelay = numpy.concatenate((tdelay, orig_tdelay + mjd*u.day))
            expected_primary = flux * dmjd
            flux_norm = expected_primary / nprimary
            weights = numpy.concatenate((weights, flux_norm*numpy.ones_like(orig_tdelay.value)))
            
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
