"""
PWN Leptonic Model: Inverse Compton Scattering

This module implements the leptonic gamma-ray emission model for PWN scenarios,
where relativistic electrons scatter background photon fields (CMB, IR, starlight)
to produce gamma-rays via Inverse Compton (IC) scattering.

Based on parameters from Hnatyk et al. 2022 (MNRAS), Table 1:
- ECBPL spectrum: Γ1 = 1.49, Γ2 = 3.04, Ebr = 4.7 GeV, Ecut = 396.7 TeV, We = 3.60e50 erg
- Alternative ECPL: Γ = 3.08, Emin = 10 GeV, Ecut = 424.3 TeV, We = 8.80e49 erg

Seed photon fields (representative for TeV PWNe in HGPS):
- CMB: T = 2.7 K, w = 0.26 eV/cm³
- IR/FIR: T = 107 K, w = 1.19 eV/cm³
- Starlight/NIR: T = 7906 K, w = 1.92 eV/cm³
"""

import numpy as np
import astropy.units as u
import naima
from naima.models import (
    ExponentialCutoffPowerLaw,
    ExponentialCutoffBrokenPowerLaw,
    InverseCompton,
)


# =============================================================================
# Seed Photon Fields from Hnatyk et al. 2022
# =============================================================================

SEED_PHOTON_FIELDS = [
    ['CMB', 2.7 * u.K, 0.26 * u.eV / u.cm**3],
    ['FIR', 107 * u.K, 1.19 * u.eV / u.cm**3],
    ['NIR', 7906 * u.K, 1.92 * u.eV / u.cm**3],
]


# =============================================================================
# Default Parameters from Hnatyk et al. 2022, Table 1
# =============================================================================

PWN_DEFAULTS = {
    # Common parameters
    'distance': 12.5 * u.kpc,
    'Ee_min': 1.0 * u.GeV,
    'Ee_max': 1e6 * u.GeV,  # 1 PeV

    # ECBPL spectrum best-fit (PWN standard)
    'ecbpl': {
        'log10_norm': 40.28,  # log10(N0 / (1/eV)) at E0
        'E0': 0.19 * u.TeV,
        'Ebr': 4.7 * u.GeV,
        'index1': 1.49,
        'index2': 3.04,
        'Ecut': 396.7 * u.TeV,
    },

    # Alternative ECPL spectrum (simpler model)
    'ecpl': {
        'log10_norm': 37.95,  # log10(N0 / (1/eV)) at E0
        'E0': 0.175 * u.TeV,
        'index': 3.08,
        'Ecut': 424.3 * u.TeV,
        'Ee_min': 10.0 * u.GeV,  # Higher minimum for this model
    },
}


# =============================================================================
# Model Functions for NAIMA Fitting
# =============================================================================

def pwn_ic_ecpl(pars, data):
    """
    Leptonic gamma-ray emission from PWN with exponential cutoff power-law
    electron spectrum (1-population model).

    This is the simpler "alternative" model from the paper with Emin = 10 GeV.

    Parameters (pars):
    -----------------
    pars[0]: log10(norm) - log10 of amplitude at E0=1 TeV in units of 1/eV
    pars[1]: index - electron spectral index (positive, typically 2.0-4.0)
    pars[2]: log10(Ecut/TeV) - log10 of cutoff energy in TeV

    Returns
    -------
    flux : Quantity
        Differential photon flux at data energies [1/(cm² s GeV)]
    """
    log10_norm, index, log10_ecut = pars

    # Check for invalid parameters
    if not np.isfinite(log10_norm) or not np.isfinite(index) or not np.isfinite(log10_ecut):
        return np.full(len(data), np.nan) * data['flux'].unit

    # Safety bounds for cutoff energy
    if log10_ecut < -1.0 or log10_ecut > 4.0:
        return np.full(len(data), np.nan) * data['flux'].unit

    # Electron spectrum parameters
    amplitude = (10.0 ** log10_norm) / u.eV
    E0 = 1.0 * u.TeV
    Ecut = (10.0 ** log10_ecut) * u.TeV

    # Create ECPL electron distribution
    electron_dist = ExponentialCutoffPowerLaw(amplitude, E0, index, Ecut)

    # Create IC model with seed photon fields
    ic = InverseCompton(
        electron_dist,
        seed_photon_fields=SEED_PHOTON_FIELDS,
        Eemin=1.0 * u.GeV,
        Eemax=PWN_DEFAULTS['Ee_max'],
    )

    # Calculate flux at observer
    flux = ic.flux(data, distance=PWN_DEFAULTS['distance'])

    return flux.to(data['flux'].unit)


def pwn_ic_ecbpl(pars, data):
    """
    Leptonic gamma-ray emission from PWN with exponential cutoff broken
    power-law electron spectrum.

    This is the standard PWN model with a break energy and two spectral indices.

    Parameters (pars):
    -----------------
    pars[0]: log10(norm) - log10 of amplitude at E0=1 TeV in units of 1/eV
    pars[1]: index1 - electron spectral index below break (typically < 2)
    pars[2]: index2 - electron spectral index above break (typically > 2)
    pars[3]: log10(Ebr/GeV) - log10 of break energy in GeV
    pars[4]: log10(Ecut/TeV) - log10 of cutoff energy in TeV

    Returns
    -------
    flux : Quantity
        Differential photon flux at data energies [1/(cm² s GeV)]
    """
    log10_norm, index1, index2, log10_ebr, log10_ecut = pars

    # Check for invalid parameters
    if not all(np.isfinite(p) for p in pars):
        return np.full(len(data), np.nan) * data['flux'].unit

    # Safety bounds
    if log10_ecut < 0.0 or log10_ecut > 4.0:
        return np.full(len(data), np.nan) * data['flux'].unit
    if log10_ebr < -1.0 or log10_ebr > 3.0:
        return np.full(len(data), np.nan) * data['flux'].unit

    # Electron spectrum parameters
    amplitude = (10.0 ** log10_norm) / u.eV
    E0 = 1.0 * u.TeV
    Ebr = (10.0 ** log10_ebr) * u.GeV
    Ecut = (10.0 ** log10_ecut) * u.TeV

    # Create ECBPL electron distribution
    electron_dist = ExponentialCutoffBrokenPowerLaw(
        amplitude, E0, Ebr, index1, index2, Ecut
    )

    # Create IC model with seed photon fields
    ic = InverseCompton(
        electron_dist,
        seed_photon_fields=SEED_PHOTON_FIELDS,
        Eemin=PWN_DEFAULTS['Ee_min'],
        Eemax=PWN_DEFAULTS['Ee_max'],
    )

    # Calculate flux at observer
    flux = ic.flux(data, distance=PWN_DEFAULTS['distance'])

    return flux.to(data['flux'].unit)


# =============================================================================
# Prior Functions
# =============================================================================

def pwn_lnprior_ecpl(pars):
    """
    Log-prior for PWN ECPL model.

    Parameters:
    - pars[0]: log10(norm) - uniform prior [30, 45]
    - pars[1]: index - uniform prior [2.0, 4.5]
    - pars[2]: log10(Ecut/TeV) - uniform prior [-1, 4] (0.1 TeV to 10 PeV)
    """
    log10_norm, index, log10_ecut = pars

    lp = 0.0
    lp += naima.uniform_prior(log10_norm, 30.0, 45.0)
    lp += naima.uniform_prior(index, 2.0, 4.5)
    lp += naima.uniform_prior(log10_ecut, -1.0, 4.0)

    return lp


def pwn_lnprior_ecbpl(pars):
    """
    Log-prior for PWN ECBPL model.

    Parameters:
    - pars[0]: log10(norm) - uniform prior [35, 50]
    - pars[1]: index1 - uniform prior [1.0, 2.5] (hard spectrum below break)
    - pars[2]: index2 - uniform prior [2.5, 4.5] (soft spectrum above break)
    - pars[3]: log10(Ebr/GeV) - uniform prior [-1, 3] (0.1 GeV to 1 TeV)
    - pars[4]: log10(Ecut/TeV) - uniform prior [1, 4] (10 TeV to 10 PeV)
    """
    log10_norm, index1, index2, log10_ebr, log10_ecut = pars

    lp = 0.0
    lp += naima.uniform_prior(log10_norm, 35.0, 50.0)
    lp += naima.uniform_prior(index1, 1.0, 2.5)
    lp += naima.uniform_prior(index2, 2.5, 4.5)
    lp += naima.uniform_prior(log10_ebr, -1.0, 3.0)
    lp += naima.uniform_prior(log10_ecut, 1.0, 4.0)

    return lp


# =============================================================================
# Helper Functions
# =============================================================================

def compute_electron_energy(pars, model='ecpl', Emin=1*u.GeV, Emax=1e6*u.GeV):
    """
    Compute total energy in electrons for given parameters.

    Parameters
    ----------
    pars : array-like
        Model parameters
    model : str
        'ecpl' or 'ecbpl'
    Emin, Emax : Quantity
        Energy integration limits

    Returns
    -------
    We : Quantity
        Total electron energy in erg
    """
    E0 = 1.0 * u.TeV

    if model == 'ecpl':
        log10_norm, index, log10_ecut = pars
        amplitude = (10.0 ** log10_norm) / u.eV
        Ecut = (10.0 ** log10_ecut) * u.TeV
        electron_dist = ExponentialCutoffPowerLaw(amplitude, E0, index, Ecut)
    elif model == 'ecbpl':
        log10_norm, index1, index2, log10_ebr, log10_ecut = pars
        amplitude = (10.0 ** log10_norm) / u.eV
        Ebr = (10.0 ** log10_ebr) * u.GeV
        Ecut = (10.0 ** log10_ecut) * u.TeV
        electron_dist = ExponentialCutoffBrokenPowerLaw(
            amplitude, E0, Ebr, index1, index2, Ecut
        )
    else:
        raise ValueError(f"Unknown model: {model}")

    # Create IC model to use compute_We
    ic = InverseCompton(electron_dist, seed_photon_fields=['CMB'])
    We = ic.compute_We(Eemin=Emin, Eemax=Emax)

    return We.to(u.erg)


def get_initial_params_ecpl():
    """Get reasonable initial parameters for ECPL model."""
    return np.array([37.0, 3.0, 2.5])  # log10(Ecut) ~ 300 TeV


def get_initial_params_ecbpl():
    """Get reasonable initial parameters for ECBPL model."""
    return np.array([40.0, 1.5, 3.0, 0.7, 2.6])
    # log10(Ebr) ~ 5 GeV, log10(Ecut) ~ 400 TeV


def get_labels_ecpl():
    """Get parameter labels for ECPL model."""
    return [
        r'$\log_{10}(N_0/\mathrm{eV}^{-1})$',
        r'$\Gamma_e$',
        r'$\log_{10}(E_\mathrm{cut}/\mathrm{TeV})$'
    ]


def get_labels_ecbpl():
    """Get parameter labels for ECBPL model."""
    return [
        r'$\log_{10}(N_0/\mathrm{eV}^{-1})$',
        r'$\Gamma_{e,1}$',
        r'$\Gamma_{e,2}$',
        r'$\log_{10}(E_\mathrm{br}/\mathrm{GeV})$',
        r'$\log_{10}(E_\mathrm{cut}/\mathrm{TeV})$'
    ]
