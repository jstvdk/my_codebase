"""
plotting.py
===========

Reusable, paper-style SED plotting functions for the SGR 1900+14 models
(Fig. 4 / Fig. 5 style of Hnatyk et al. 2022).

**The whole point:** each plotting function takes a *parameter vector* as its first
argument, so you can drop in the best-fit values from a fitting notebook and see
the figure immediately. For example, at the end of `fit_leptonic_inverse_compton`:

    from spectrum_tools import load_spectrum
    from plotting import plot_leptonic_sed

    q50 = np.percentile(sampler.get_chain(flat=True), 50, axis=0)   # your fit
    data = load_spectrum('../spectra/combined_real_baseline.ecsv')
    hawc = load_spectrum('../spectra/hawc_3hwc_propagated.ecsv')
    plot_leptonic_sed(q50, data=data, hawc=hawc)

Pass the paper / module defaults (`hadronic.INITIAL`, `leptonic.INITIAL`) to
reproduce the published figures instead.

Every function returns the matplotlib ``Axes`` it drew on, so they compose (e.g.
into a multi-panel figure) and you can keep customising afterwards.
"""

from __future__ import annotations

import numpy as np
import astropy.units as u
import matplotlib.pyplot as plt
from naima.models import Synchrotron, InverseCompton

from naima_models import hadronic as H, leptonic as L


# Default photon-energy grid for the model curves (1 MeV .. 1 PeV) and SED unit.
DEFAULT_EGRID = np.logspace(6, 15, 300) * u.eV
SED_UNIT = u.Unit("erg / (cm2 s)")

# Marker style per instrument for the data points.
_POINT_STYLE = {
    "Fermi-LAT": ("tab:blue", "o"),
    "H.E.S.S.": ("tab:green", "s"),
    "HAWC": ("tab:red", "^"),
}


# =============================================================================
# Low-level helpers
# =============================================================================

def _sed(energy, flux):
    """E^2 dN/dE in erg cm^-2 s^-1 (plain numpy values for plotting)."""
    return (energy ** 2 * flux).to(SED_UNIT).value


def sed_axes(ax=None, title=None, xlim=(1e6, 1e15), ylim=(1e-14, 1e-10)):
    """Create (or configure) a log-log SED axis in the paper's style."""
    if ax is None:
        _, ax = plt.subplots(figsize=(8.5, 6))
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Energy [eV]", fontsize=12)
    ax.set_ylabel(r"$E^2\,dN/dE\;\;[\mathrm{erg\,cm^{-2}\,s^{-1}}]$", fontsize=12)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    if title:
        ax.set_title(title, fontsize=13)
    ax.grid(which="both", ls=":", alpha=0.35)
    return ax


def plot_points(ax, table, color="k", marker="o", label=None):
    """Plot one spectrum table as SED points; upper limits become down-arrows."""
    E = table["energy"].to(u.eV).value
    y = _sed(table["energy"], table["flux"])
    ye = _sed(table["energy"], table["flux_error_hi"])
    ul = np.asarray(table["ul"]) if "ul" in table.colnames else np.zeros(len(table), bool)
    ax.errorbar(E[~ul], y[~ul], yerr=ye[~ul], fmt=marker, color=color, ms=5,
                capsize=2, ls="none", label=label, zorder=10)
    if ul.any():
        ax.errorbar(E[ul], y[ul], yerr=0.35 * y[ul], uplims=True, fmt=marker,
                    color=color, ms=5, ls="none", zorder=10)


def plot_observed(ax, data=None, hawc=None):
    """
    Overlay observed data. ``data`` may be a combined table (split by the
    ``instrument`` column) or a single-instrument table; ``hawc`` is an optional
    extra (comparison-only) table.
    """
    if data is not None:
        if "instrument" in data.colnames:
            inst = np.array(data["instrument"])
            for name in dict.fromkeys(inst):
                color, marker = _POINT_STYLE.get(name, ("0.3", "o"))
                plot_points(ax, data[inst == name], color=color, marker=marker, label=name)
        else:
            plot_points(ax, data, label="data")
    if hawc is not None:
        plot_points(ax, hawc, color="tab:red", marker="^", label="HAWC (not fitted)")


# =============================================================================
# Model SED plots -- pass a parameter vector (e.g. your fitted medians)
# =============================================================================

def plot_hadronic_sed(pars, data=None, hawc=None, ax=None, egrid=DEFAULT_EGRID,
                      sync_B=(1, 5), components=True,
                      title="SGR 1900+14 region -- hadronic (SNR) model"):
    """
    Paper Fig. 4-style SED for the hadronic model at parameter vector ``pars``
    (``[log10 N0_p, Gamma_p, log10(Ecut/TeV), Kep, n_H]``).

    Draws the total, the PionDecay curve (legend shows W_p), and -- if
    ``components`` -- the IC components (CMB/IR/NIR) and Synchrotron at the fields
    in ``sync_B`` [microgauss]. Optionally overlays ``data``/``hawc`` points.
    Returns the Axes.
    """
    distance = H.CONFIG["distance"]
    ax = sed_axes(ax, title)
    plot_observed(ax, data, hawc)

    comps = H.build_models(pars)
    edist = H.electron_distribution(pars)
    f_pion = comps["pion"].flux(egrid, distance=distance)
    f_ic = comps["ic"].flux(egrid, distance=distance)
    f_total = f_pion + f_ic
    Wp = H.compute_Wp(pars)

    ax.plot(egrid.to(u.eV), _sed(egrid, f_total), "k-", lw=2.5, label="Total")
    ax.plot(egrid.to(u.eV), _sed(egrid, f_pion), color="purple", lw=2,
            label=f"PionDecay ($W_p$={Wp.to('erg').value:.2e} erg)")
    if components:
        for (name, T, w), ls in zip(H.SEED_PHOTON_FIELDS, ["--", "-.", ":"]):
            fic = InverseCompton(edist, seed_photon_fields=[[name, T, w]],
                                 Eemin=H.CONFIG["Ee_min"], Eemax=H.CONFIG["Ee_max"]
                                 ).flux(egrid, distance=distance)
            ax.plot(egrid.to(u.eV), _sed(egrid, fic), ls, color="darkorange", lw=1.2,
                    label=f"IC ({name})")
        for b, ls in zip(sync_B, ["--", ":"]):
            fs = Synchrotron(edist, B=b * u.uG, Eemin=H.CONFIG["Ee_min"],
                             Eemax=H.CONFIG["Ee_max"]).flux(egrid, distance=distance)
            ax.plot(egrid.to(u.eV), _sed(egrid, fs), ls, color="steelblue", lw=1.2,
                    label=f"Synchrotron (B={b} $\\mu$G)")
    ax.legend(fontsize=8, ncol=2, loc="lower center")
    return ax


def plot_leptonic_sed(pars, data=None, hawc=None, ax=None, egrid=DEFAULT_EGRID,
                      sync_B=(1, 5), components=True,
                      title="SGR 1900+14 region -- leptonic (PWN) model"):
    """
    Paper Fig. 5-style SED for the leptonic model at parameter vector ``pars``
    (``[log10 N0_e, Gamma_e, log10(Ecut/TeV)]``).

    Draws the total Inverse Compton (legend shows W_e), and -- if ``components``
    -- the IC per seed field (CMB/FIR/NIR) and Synchrotron at ``sync_B`` [uG].
    Returns the Axes.
    """
    distance = L.CONFIG["distance"]
    ax = sed_axes(ax, title)
    plot_observed(ax, data, hawc)

    comps = L.build_models(pars)
    edist = L.electron_distribution(pars)
    f_ic = comps["ic"].flux(egrid, distance=distance)
    We = L.compute_We(pars)

    ax.plot(egrid.to(u.eV), _sed(egrid, f_ic), "k-", lw=2.5,
            label=f"Total IC ($W_e$={We.to('erg').value:.2e} erg)")
    if components:
        for (name, fic), ls in zip(L.ic_components(pars, egrid).items(), ["--", "-.", ":"]):
            ax.plot(egrid.to(u.eV), _sed(egrid, fic), ls, color="darkorange", lw=1.2,
                    label=f"IC ({name})")
        for b, ls in zip(sync_B, ["--", ":"]):
            fs = Synchrotron(edist, B=b * u.uG, Eemin=L.CONFIG["Ee_min"],
                             Eemax=L.CONFIG["Ee_max"]).flux(egrid, distance=distance)
            ax.plot(egrid.to(u.eV), _sed(egrid, fs), ls, color="steelblue", lw=1.2,
                    label=f"Synchrotron (B={b} $\\mu$G)")
    ax.legend(fontsize=8, ncol=2, loc="lower center")
    return ax


def plot_comparison(had_pars, lep_pars, data=None, hawc=None, egrid=DEFAULT_EGRID,
                    components=False):
    """
    Side-by-side hadronic vs leptonic SED for the two parameter vectors.
    Returns ``(fig, axes)``. With ``components=False`` (default) only the totals
    are shown, for a clean comparison.
    """
    fig, axes = plt.subplots(1, 2, figsize=(15, 6), sharex=True, sharey=True)
    plot_hadronic_sed(had_pars, data=data, hawc=hawc, ax=axes[0], egrid=egrid,
                      components=components, title="Hadronic (SNR)")
    plot_leptonic_sed(lep_pars, data=data, hawc=hawc, ax=axes[1], egrid=egrid,
                      components=components, title="Leptonic (PWN)")
    axes[1].set_ylabel("")
    fig.tight_layout()
    return fig, axes
