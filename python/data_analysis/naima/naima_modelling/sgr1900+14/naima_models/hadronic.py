"""
hadronic.py
===========

Hadronic gamma-ray emission model for the SGR 1900+14 region, following
Hnatyk et al. 2022 (MNRAS 516, 4196).

Physical picture
----------------
Cosmic-ray **protons** accelerated at the shock follow an exponential-cutoff
power law (ECPL).  They interact with ambient gas (density ``n_H``) and produce
gamma rays through neutral-pion decay (pp -> pi0 -> gamma gamma).  A population
of **electrons co-accelerated** with the protons is included as well, with the
*same spectral shape* but normalisation scaled down by the electron-to-proton
energy fraction ``Kep`` (so N0_e = Kep * N0_p, hence We = Kep * Wp).  These
electrons add sub-dominant Inverse-Compton and Synchrotron emission.

Total model flux  =  PionDecay  +  InverseCompton(e-)  +  Synchrotron(e-)

In the GeV-TeV band the pion-decay term dominates; IC and synchrotron are tiny
here (synchrotron peaks in radio/X-rays) but are carried along so the same
model can be plotted across the whole SED.

Free parameters (this implementation)
-------------------------------------
    pars[0]  log10(N0_p / eV^-1)   proton normalisation at E0 = 1 TeV
    pars[1]  Gamma_p               proton spectral index
    pars[2]  log10(E_cut / TeV)    proton cutoff energy
    pars[3]  Kep                   electron-to-proton energy fraction
    pars[4]  n_H [cm^-3]           ambient gas density

Important degeneracy (teaching point)
-------------------------------------
The pion-decay flux scales as N0_p * n_H, so the gamma-ray data constrain only
the *product*.  With both ``N0_p`` and ``n_H`` free the marginal posteriors of
each are broad and anti-correlated (a "banana"); only their product -- and
therefore Wp * n_H -- is well measured.  We keep n_H free (as requested) and
flag this explicitly in the notebook.
"""

from __future__ import annotations

import numpy as np
import astropy.units as u
import naima
from naima.models import ExponentialCutoffPowerLaw, PionDecay, InverseCompton, Synchrotron


# =============================================================================
# Fixed configuration (Hnatyk et al. 2022)
# =============================================================================

CONFIG = {
    "distance": 12.5 * u.kpc,
    "E0": 1.0 * u.TeV,            # reference energy for the normalisation N0
    "Ep_min": 1.0 * u.GeV,       # proton integration / Wp lower bound
    "Ep_max": 1e6 * u.GeV,       # 1 PeV
    "Ee_min": 1.0 * u.GeV,       # electron integration lower bound
    "Ee_max": 1e6 * u.GeV,
    "B": 3.0 * u.uG,             # ambient magnetic field (fixed) for synchrotron
}

# Seed photon fields for the electron IC component (CMB + IR + starlight).
SEED_PHOTON_FIELDS = [
    ["CMB", 2.7 * u.K, 0.26 * u.eV / u.cm**3],
    ["FIR", 107 * u.K, 1.19 * u.eV / u.cm**3],
    ["NIR", 7906 * u.K, 1.92 * u.eV / u.cm**3],
]

# Initial guess and labels (paper ECPL hadronic best fit, normalisation
# re-referenced from the paper's E0=0.78 TeV to our E0=1 TeV; n_H = paper nsh).
INITIAL = np.array([36.89, 2.41, np.log10(185.2), 0.0041, 9.81])
LABELS = [
    r"$\log_{10}(N_{0,p}/\mathrm{eV}^{-1})$",
    r"$\Gamma_p$",
    r"$\log_{10}(E_\mathrm{cut}/\mathrm{TeV})$",
    r"$K_\mathrm{ep}$",
    r"$n_\mathrm{H}\;[\mathrm{cm}^{-3}]$",
]


# =============================================================================
# Build the radiative models from a parameter vector
# =============================================================================

def _unpack(pars):
    """Return (proton_dist, electron_dist, n_H) from a parameter vector."""
    log10_norm, index, log10_ecut, kep, nh = pars

    amplitude_p = (10.0 ** log10_norm) / u.eV
    e_cut = (10.0 ** log10_ecut) * u.TeV

    proton_dist = ExponentialCutoffPowerLaw(amplitude_p, CONFIG["E0"], index, e_cut)
    # Co-accelerated electrons: same shape, amplitude scaled by Kep.
    electron_dist = ExponentialCutoffPowerLaw(kep * amplitude_p, CONFIG["E0"], index, e_cut)

    return proton_dist, electron_dist, nh * u.Unit("cm-3")


def build_models(pars):
    """
    Construct the three radiative components (PionDecay, IC, Synchrotron).

    Returns a dict with keys 'pion', 'ic', 'sync' -- useful both for the fit
    (sum the fluxes) and for plotting the components separately.
    """
    proton_dist, electron_dist, nh = _unpack(pars)

    pion = PionDecay(
        proton_dist, nh=nh,
        Epmin=CONFIG["Ep_min"], Epmax=CONFIG["Ep_max"],
    )
    ic = InverseCompton(
        electron_dist, seed_photon_fields=SEED_PHOTON_FIELDS,
        Eemin=CONFIG["Ee_min"], Eemax=CONFIG["Ee_max"],
    )
    sync = Synchrotron(
        electron_dist, B=CONFIG["B"],
        Eemin=CONFIG["Ee_min"], Eemax=CONFIG["Ee_max"],
    )
    return {"pion": pion, "ic": ic, "sync": sync}


# =============================================================================
# naima model function (total flux at the data energies)
# =============================================================================

def hadronic_model(pars, data):
    """
    Total hadronic+secondary-leptonic differential photon flux at ``data``.

    Signature matches what ``naima.run_sampler`` expects: ``model(pars, data)``
    returning a flux Quantity aligned with ``data['energy']``.
    """
    if not np.all(np.isfinite(pars)):
        return np.full(len(data), np.nan) * data["flux"].unit

    energy = data["energy"]
    models = build_models(pars)
    flux = (
        models["pion"].flux(energy, distance=CONFIG["distance"])
        + models["ic"].flux(energy, distance=CONFIG["distance"])
        + models["sync"].flux(energy, distance=CONFIG["distance"])
    )
    return flux.to(data["flux"].unit)


def lnprior(pars):
    """
    Log-prior (uniform/flat) for the hadronic ECPL parameters.

        log10(N0_p)  in [30, 42]
        Gamma_p      in [1.5, 3.5]
        log10(Ecut)  in [0, 3.5]    (1 TeV .. ~3 PeV)
        Kep          in [0, 0.1]
        n_H          in [1, 50] cm^-3
    """
    log10_norm, index, log10_ecut, kep, nh = pars
    lp = (
        naima.uniform_prior(log10_norm, 30.0, 42.0)
        + naima.uniform_prior(index, 1.5, 3.5)
        + naima.uniform_prior(log10_ecut, 0.0, 3.5)
        + naima.uniform_prior(kep, 0.0, 0.1)
        + naima.uniform_prior(nh, 1.0, 50.0)
    )
    return lp


# =============================================================================
# Derived quantities
# =============================================================================

def electron_distribution(pars):
    """The co-accelerated electron ECPL (amplitude = Kep * proton amplitude)."""
    _, electron_dist, _ = _unpack(pars)
    return electron_dist


def compute_Wp(pars, Emin=None, Emax=None):
    """Total energy in protons (erg) over [Emin, Emax] (defaults: 1 GeV..1 PeV)."""
    proton_dist, _, nh = _unpack(pars)
    pion = PionDecay(proton_dist, nh=nh)
    Emin = CONFIG["Ep_min"] if Emin is None else Emin
    Emax = CONFIG["Ep_max"] if Emax is None else Emax
    return pion.compute_Wp(Epmin=Emin, Epmax=Emax).to(u.erg)


def compute_We(pars, Emin=None, Emax=None):
    """Total energy in co-accelerated electrons (erg). Equals Kep * Wp by design."""
    _, electron_dist, _ = _unpack(pars)
    ic = InverseCompton(electron_dist, seed_photon_fields=["CMB"])
    Emin = CONFIG["Ee_min"] if Emin is None else Emin
    Emax = CONFIG["Ee_max"] if Emax is None else Emax
    return ic.compute_We(Eemin=Emin, Eemax=Emax).to(u.erg)
