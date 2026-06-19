"""
leptonic.py
===========

Leptonic gamma-ray emission model for the SGR 1900+14 region, following
Hnatyk et al. 2022 (MNRAS 516, 4196).

Physical picture
----------------
A single population of relativistic **electrons** with an exponential-cutoff
power-law (ECPL) spectrum up-scatters ambient photon fields (CMB + infrared +
starlight) to gamma-ray energies via **Inverse Compton** (IC).  A Synchrotron
component (fixed B) from the same electrons is carried along for the full-SED
plot; it is negligible in the GeV-TeV band.

Total model flux  =  InverseCompton(e-)  +  Synchrotron(e-)

This is the "alternative ECPL" PWN model of the paper (Table 1), for which
We = 8.80e49 erg with E_e,min = 10 GeV.

Free parameters
---------------
    pars[0]  log10(N0_e / eV^-1)   electron normalisation at E0 = 1 TeV
    pars[1]  Gamma_e               electron spectral index
    pars[2]  log10(E_cut / TeV)    electron cutoff energy
"""

from __future__ import annotations

import numpy as np
import astropy.units as u
import naima
from naima.models import ExponentialCutoffPowerLaw, InverseCompton, Synchrotron


# =============================================================================
# Fixed configuration (Hnatyk et al. 2022)
# =============================================================================

CONFIG = {
    "distance": 12.5 * u.kpc,
    "E0": 1.0 * u.TeV,
    # Paper's "alternative ECPL" PWN model uses E_e,min = 10 GeV; keeping the
    # same bound here reproduces its We = 8.80e49 erg.
    "Ee_min": 10.0 * u.GeV,
    "Ee_max": 1e6 * u.GeV,
    "B": 3.0 * u.uG,             # fixed; synchrotron only matters at low E
}

SEED_PHOTON_FIELDS = [
    ["CMB", 2.7 * u.K, 0.26 * u.eV / u.cm**3],
    ["FIR", 107 * u.K, 1.19 * u.eV / u.cm**3],
    ["NIR", 7906 * u.K, 1.92 * u.eV / u.cm**3],
]

# Initial guess and labels (paper alternative-ECPL PWN best fit, normalisation
# re-referenced from the paper's E0=0.175 TeV to our E0=1 TeV).
INITIAL = np.array([35.62, 3.08, np.log10(424.3)])
LABELS = [
    r"$\log_{10}(N_{0,e}/\mathrm{eV}^{-1})$",
    r"$\Gamma_e$",
    r"$\log_{10}(E_\mathrm{cut}/\mathrm{TeV})$",
]


# =============================================================================
# Build the radiative models
# =============================================================================

def _electron_dist(pars):
    log10_norm, index, log10_ecut = pars
    amplitude = (10.0 ** log10_norm) / u.eV
    e_cut = (10.0 ** log10_ecut) * u.TeV
    return ExponentialCutoffPowerLaw(amplitude, CONFIG["E0"], index, e_cut)


def build_models(pars):
    """Return dict with 'ic' (InverseCompton) and 'sync' (Synchrotron)."""
    electron_dist = _electron_dist(pars)
    ic = InverseCompton(
        electron_dist, seed_photon_fields=SEED_PHOTON_FIELDS,
        Eemin=CONFIG["Ee_min"], Eemax=CONFIG["Ee_max"],
    )
    sync = Synchrotron(
        electron_dist, B=CONFIG["B"],
        Eemin=CONFIG["Ee_min"], Eemax=CONFIG["Ee_max"],
    )
    return {"ic": ic, "sync": sync}


def ic_components(pars, energy):
    """
    Per-seed-field IC flux (CMB, FIR, NIR) at ``energy`` -- for plotting the
    individual IC contributions in the SED.
    """
    electron_dist = _electron_dist(pars)
    out = {}
    for name, T, w in SEED_PHOTON_FIELDS:
        ic = InverseCompton(
            electron_dist, seed_photon_fields=[[name, T, w]],
            Eemin=CONFIG["Ee_min"], Eemax=CONFIG["Ee_max"],
        )
        out[name] = ic.flux(energy, distance=CONFIG["distance"])
    return out


# =============================================================================
# naima model function
# =============================================================================

def leptonic_model(pars, data):
    """Total leptonic (IC + Synchrotron) differential photon flux at ``data``."""
    if not np.all(np.isfinite(pars)):
        return np.full(len(data), np.nan) * data["flux"].unit

    energy = data["energy"]
    models = build_models(pars)
    flux = (
        models["ic"].flux(energy, distance=CONFIG["distance"])
        + models["sync"].flux(energy, distance=CONFIG["distance"])
    )
    return flux.to(data["flux"].unit)


def lnprior(pars):
    """
    Log-prior (flat) for the leptonic ECPL parameters.

        log10(N0_e)  in [30, 45]
        Gamma_e      in [2.0, 4.5]
        log10(Ecut)  in [-1, 4]    (0.1 TeV .. 10 PeV)
    """
    log10_norm, index, log10_ecut = pars
    lp = (
        naima.uniform_prior(log10_norm, 30.0, 45.0)
        + naima.uniform_prior(index, 2.0, 4.5)
        + naima.uniform_prior(log10_ecut, -1.0, 4.0)
    )
    return lp


# =============================================================================
# Derived quantities
# =============================================================================

def electron_distribution(pars):
    """The electron ECPL distribution for this parameter vector."""
    return _electron_dist(pars)


def compute_We(pars, Emin=None, Emax=None):
    """Total energy in electrons (erg) over [Emin, Emax] (defaults: 10 GeV..1 PeV)."""
    electron_dist = _electron_dist(pars)
    ic = InverseCompton(electron_dist, seed_photon_fields=["CMB"])
    Emin = CONFIG["Ee_min"] if Emin is None else Emin
    Emax = CONFIG["Ee_max"] if Emax is None else Emax
    return ic.compute_We(Eemin=Emin, Eemax=Emax).to(u.erg)
