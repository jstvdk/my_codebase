"""
naima_models: emission models for the SGR 1900+14 region
========================================================

Two scenarios, following Hnatyk et al. 2022 (MNRAS 516, 4196):

- :mod:`naima_models.hadronic` -- proton ECPL -> PionDecay, plus co-accelerated
  electrons (Kep) contributing Inverse Compton + Synchrotron.
- :mod:`naima_models.leptonic` -- electron ECPL -> Inverse Compton (+ Synchrotron).

Each module exposes the same small interface:
    <model>_model(pars, data)   ->  total flux Quantity (for naima.run_sampler)
    lnprior(pars)               ->  flat log-prior
    build_models(pars)          ->  dict of radiative components (for plotting)
    compute_Wp / compute_We     ->  total particle energy in erg
    INITIAL, LABELS, CONFIG, SEED_PHOTON_FIELDS
"""

from . import hadronic, leptonic

__all__ = ["hadronic", "leptonic"]
