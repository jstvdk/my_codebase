"""
Naima Models for SGR 1900+14 Region Gamma-Ray Analysis

This module provides naima model functions for fitting gamma-ray spectra
following the methodology from Hnatyk et al. 2022 (MNRAS).

Models included:
- SNR (Hadronic): Pion decay from proton-proton interactions
- PWN (Leptonic): Inverse Compton scattering from electron populations

Reference: Hnatyk et al. 2022, MNRAS, "Unveiling the nature of the unidentified
gamma-ray sources 4FGL J1908.6+0915e, HESS J1907+089/HOTS J1907+091, and
3HWC J1907+085 in the sky region of the magnetar SGR 1900+14"
"""

from .snr_pion_decay import (
    snr_pion_decay_pl,
    snr_pion_decay_ecpl,
    snr_lnprior_pl,
    snr_lnprior_ecpl,
    SNR_DEFAULTS,
)

from .pwn_inverse_compton import (
    pwn_ic_ecpl,
    pwn_ic_ecbpl,
    pwn_lnprior_ecpl,
    pwn_lnprior_ecbpl,
    PWN_DEFAULTS,
    SEED_PHOTON_FIELDS,
)

__all__ = [
    # SNR models
    'snr_pion_decay_pl',
    'snr_pion_decay_ecpl',
    'snr_lnprior_pl',
    'snr_lnprior_ecpl',
    'SNR_DEFAULTS',
    # PWN models
    'pwn_ic_ecpl',
    'pwn_ic_ecbpl',
    'pwn_lnprior_ecpl',
    'pwn_lnprior_ecbpl',
    'PWN_DEFAULTS',
    'SEED_PHOTON_FIELDS',
]
