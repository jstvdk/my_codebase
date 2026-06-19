import numpy as np
import astropy.units as u
import naima
from naima.models import ExponentialCutoffPowerLaw, InverseCompton

# mymodels.py
import numpy as np
import astropy.units as u
import naima
from naima.models import ExponentialCutoffPowerLaw, InverseCompton

DIST = 12.5 * u.kpc  # your source distance

def electron_ic(pars, data):
    """
    pars = [log10A, index, log10(Ecut/TeV)]
    returns flux array with same unit/shape as data['flux']
    """
    log10A, alpha, log10ecut = pars
    if not np.isfinite(log10A) or not np.isfinite(log10ecut):
        return np.full(len(data), np.nan) * data["flux"].unit
    if (log10ecut < -1.5) or (log10ecut > 3.0):   # safety box: 0.03–1000 TeV
        return np.full(len(data), np.nan) * data["flux"].unit

    amp   = (10.0**log10A) / u.eV
    ecut  = (10.0**log10ecut) * u.TeV
    ecpl  = ExponentialCutoffPowerLaw(amp, 1.0*u.TeV, alpha, ecut)

    ic = InverseCompton(
        ecpl,
        seed_photon_fields=[
            ["CMB", 2.7*u.K, 0.26 * u.eV/u.cm**3],
            ["FIR", 107*u.K, 1.19 * u.eV/u.cm**3],
            ["NIR", 7906*u.K, 1.92 * u.eV/u.cm**3],  # enable if appropriate
        ],
        Eemin=10.0*u.GeV,
    )

    f = ic.flux(data, distance=DIST)  # returns 1/(cm2 s energy_unit)
    # choose output unit
    if "flux" in data.colnames:
        target = data["flux"].unit
    else:
        target = 1 / (u.cm**2 * u.s * data["energy"].unit)
    return f.to(target)
    #return ic.flux(data, distance=DIST).to(data["flux"].unit)

def lnprior(pars):
    log10A, alpha, log10ecut = pars
    lp  = naima.uniform_prior(log10A,    28.0, 40.0)  # 10^28..10^40 1/eV (wide for 12.5 kpc)
    lp += naima.uniform_prior(alpha,      1.2,  4.0)
    lp += naima.uniform_prior(log10ecut, -1.0,  3.0)  # 0.1..1000 TeV
    return lp
