"""
SNR Hadronic Model: Pion Decay from Proton-Proton Interactions

This module implements the hadronic gamma-ray emission model for SNR scenarios,
where cosmic ray protons interact with ambient medium protons producing neutral
pions that decay into gamma-rays.

Based on parameters from Hnatyk et al. 2022 (MNRAS), Table 1:
- PL spectrum: Γcr = 2.55, Wp = 5.03e50 erg
- ECPL spectrum: Γcr = 2.41, Ecut = 185.2 TeV, Wp = 5.12e50 erg

The model uses naima.models.PionDecay for gamma-ray production.
"""

import numpy as np
import astropy.units as u
import naima
from naima.models import (
    PowerLaw,
    ExponentialCutoffPowerLaw,
    PionDecay,
)


# =============================================================================
# Default Parameters from Hnatyk et al. 2022, Table 1
# =============================================================================

SNR_DEFAULTS = {
    # Common parameters
    'distance': 12.5 * u.kpc,
    'Ecr_min': 1.0 * u.GeV,
    'Ecr_max': 1e6 * u.GeV,  # 1 PeV
    'nH': 10.0 * u.Unit('cm-3'),  # target density (shell)

    # PL spectrum best-fit
    'pl': {
        'log10_norm': 35.07,  # log10(N0 / (1/eV)) at E0
        'E0': 3.93 * u.TeV,
        'index': 2.55,
        'Kep': 0.02,  # electron-to-proton ratio (fixed in paper)
    },

    # ECPL spectrum best-fit
    'ecpl': {
        'log10_norm': 37.15,  # log10(N0 / (1/eV)) at E0
        'E0': 0.78 * u.TeV,
        'index': 2.41,
        'Ecut': 185.2 * u.TeV,
        'Kep': 0.0041,
    },
}


# =============================================================================
# Model Functions for NAIMA Fitting
# =============================================================================

def snr_pion_decay_pl(pars, data):
    """
    Hadronic gamma-ray emission from SNR with power-law proton spectrum.

    Parameters (pars):
    -----------------
    pars[0]: log10(norm) - log10 of amplitude at E0=1 TeV in units of 1/eV
    pars[1]: index - proton spectral index (positive, typically 2.0-3.0)

    Returns
    -------
    flux : Quantity
        Differential photon flux at data energies [1/(cm² s GeV)]
    """
    log10_norm, index = pars

    # Check for invalid parameters
    if not np.isfinite(log10_norm) or not np.isfinite(index):
        return np.full(len(data), np.nan) * data['flux'].unit

    # Proton spectrum parameters
    amplitude = (10.0 ** log10_norm) / u.eV
    E0 = 1.0 * u.TeV  # Reference energy

    # Create power-law proton distribution
    proton_dist = PowerLaw(amplitude, E0, index)

    # Create pion decay model
    pion = PionDecay(
        proton_dist,
        nh=SNR_DEFAULTS['nH'],
        Epmin=SNR_DEFAULTS['Ecr_min'],
        Epmax=SNR_DEFAULTS['Ecr_max'],
    )

    # Calculate flux at observer
    flux = pion.flux(data, distance=SNR_DEFAULTS['distance'])

    return flux.to(data['flux'].unit)


def snr_pion_decay_ecpl(pars, data):
    """
    Hadronic gamma-ray emission from SNR with exponential cutoff power-law
    proton spectrum.

    Parameters (pars):
    -----------------
    pars[0]: log10(norm) - log10 of amplitude at E0=1 TeV in units of 1/eV
    pars[1]: index - proton spectral index (positive, typically 2.0-3.0)
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

    # Proton spectrum parameters
    amplitude = (10.0 ** log10_norm) / u.eV
    E0 = 1.0 * u.TeV
    Ecut = (10.0 ** log10_ecut) * u.TeV

    # Create exponential cutoff power-law proton distribution
    proton_dist = ExponentialCutoffPowerLaw(amplitude, E0, index, Ecut)

    # Create pion decay model
    pion = PionDecay(
        proton_dist,
        nh=SNR_DEFAULTS['nH'],
        Epmin=SNR_DEFAULTS['Ecr_min'],
        Epmax=SNR_DEFAULTS['Ecr_max'],
    )

    # Calculate flux at observer
    flux = pion.flux(data, distance=SNR_DEFAULTS['distance'])

    return flux.to(data['flux'].unit)


# =============================================================================
# Prior Functions
# =============================================================================

def snr_lnprior_pl(pars):
    """
    Log-prior for SNR power-law model.

    Parameters:
    - pars[0]: log10(norm) - uniform prior [30, 40]
    - pars[1]: index - uniform prior [1.5, 3.5]
    """
    log10_norm, index = pars

    lp = 0.0
    lp += naima.uniform_prior(log10_norm, 30.0, 40.0)
    lp += naima.uniform_prior(index, 1.5, 3.5)

    return lp


def snr_lnprior_ecpl(pars):
    """
    Log-prior for SNR ECPL model.

    Parameters:
    - pars[0]: log10(norm) - uniform prior [30, 42]
    - pars[1]: index - uniform prior [1.5, 3.5]
    - pars[2]: log10(Ecut/TeV) - uniform prior [0, 3] (1 TeV to 1 PeV)
    """
    log10_norm, index, log10_ecut = pars

    lp = 0.0
    lp += naima.uniform_prior(log10_norm, 30.0, 42.0)
    lp += naima.uniform_prior(index, 1.5, 3.5)
    lp += naima.uniform_prior(log10_ecut, 0.0, 3.0)

    return lp


# =============================================================================
# Helper Functions
# =============================================================================

def compute_proton_energy(pars, model='ecpl', Emin=1*u.GeV, Emax=1e6*u.GeV):
    """
    Compute total energy in protons for given parameters.

    Parameters
    ----------
    pars : array-like
        Model parameters
    model : str
        'pl' or 'ecpl'
    Emin, Emax : Quantity
        Energy integration limits

    Returns
    -------
    Wp : Quantity
        Total proton energy in erg
    """
    E0 = 1.0 * u.TeV

    if model == 'pl':
        log10_norm, index = pars
        amplitude = (10.0 ** log10_norm) / u.eV
        proton_dist = PowerLaw(amplitude, E0, index)
    elif model == 'ecpl':
        log10_norm, index, log10_ecut = pars
        amplitude = (10.0 ** log10_norm) / u.eV
        Ecut = (10.0 ** log10_ecut) * u.TeV
        proton_dist = ExponentialCutoffPowerLaw(amplitude, E0, index, Ecut)
    else:
        raise ValueError(f"Unknown model: {model}")

    # Create pion decay just to use its compute_Wp method
    pion = PionDecay(proton_dist, nh=1*u.Unit('cm-3'))

    Wp = pion.compute_Wp(Epmin=Emin, Epmax=Emax)

    return Wp.to(u.erg)


def get_initial_params_pl():
    """Get reasonable initial parameters for PL model."""
    return np.array([35.0, 2.5])


def get_initial_params_ecpl():
    """Get reasonable initial parameters for ECPL model."""
    return np.array([37.0, 2.4, 2.3])  # log10(Ecut) ~ 200 TeV


def get_labels_pl():
    """Get parameter labels for PL model."""
    return [r'$\log_{10}(N_0/\mathrm{eV}^{-1})$', r'$\Gamma_p$']


def get_labels_ecpl():
    """Get parameter labels for ECPL model."""
    return [
        r'$\log_{10}(N_0/\mathrm{eV}^{-1})$',
        r'$\Gamma_p$',
        r'$\log_{10}(E_\mathrm{cut}/\mathrm{TeV})$'
    ]
