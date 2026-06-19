# electron_ic_model.py
import naima
from naima.models import ExponentialCutoffPowerLaw, InverseCompton
import astropy.units as u

DIST = 4.5 * u.kpc
SEED_FIELDS = [
    "CMB",
    ["FIR", 26.5 * u.K, 0.415 * u.eV / u.cm**3],
    ["NIR", 2850 * u.K, 0.46 * u.eV / u.cm**3],
]

def ElectronIC(pars, data_table):
    log10_norm, index, log10_cut = pars
    norm = 10**log10_norm / u.eV
    e0   = 1.0 * u.TeV
    ecut = (10**log10_cut) * u.TeV

    ECPL = ExponentialCutoffPowerLaw(norm, e0, index, ecut)
    IC   = InverseCompton(ECPL, seed_photon_fields=SEED_FIELDS)
    model = IC.flux(data_table["energy"], distance=DIST)
    return model.to(data_table["flux"].unit)


def lnprior(pars):
    log10_norm, index, log10_cut = pars
    lp = 0.0
    lp += naima.uniform_prior(log10_norm, 30, 40)   # norm ~ 1e30–1e40 1/eV
    lp += naima.uniform_prior(index, 1.0, 3.5)      # electron index
    lp += naima.uniform_prior(log10_cut, 2.0, 6.0)  # E_cut ~ 0.1–1e6 TeV (very wide)
    return lp