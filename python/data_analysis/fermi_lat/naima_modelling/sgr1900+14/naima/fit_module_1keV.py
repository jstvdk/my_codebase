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

E0 = 1.0*u.TeV  # or 10 GeV, both fine
def electron_ic(pars, data):
    log10A, alpha, log10ecut = pars
    A    = (10.0**log10A)/u.eV
    Ecut = (10.0**log10ecut)*u.TeV
    ecpl = ExponentialCutoffPowerLaw(A, E0, alpha, Ecut)
    ic = InverseCompton(
        ecpl,
        seed_photon_fields=[
            ["CMB", 2.7*u.K, 0.26*u.eV/u.cm**3],
            ["FIR", 107*u.K, 1.19*u.eV/u.cm**3],
            ["NIR", 7906*u.K, 1.92*u.eV/u.cm**3],  # important for sub-GeV γ
        ],
        Eemin=10.0*u.MeV,  # <-- lower electron threshold so IC reaches 1 keV
    )
    f = ic.flux(data, distance=12.5*u.kpc)
    target = data["flux"].unit if "flux" in data.colnames else 1/(u.cm**2*u.s*data["energy"].unit)
    return f.to(target)

def lnprior(pars):
    log10A, alpha, log10ecut = pars
    lp  = naima.uniform_prior(log10A,    28.0, 40.0)  # 10^28..10^40 1/eV (wide for 12.5 kpc)
    lp += naima.uniform_prior(alpha,      1.2,  4.0)
    lp += naima.uniform_prior(log10ecut, -1.0,  3.0)  # 0.1..1000 TeV
    return lp
