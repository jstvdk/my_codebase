"""
spectrum_tools.py
=================

Tools to build *standardised*, naima-ready gamma-ray spectra for the
SGR 1900+14 region, reproducing the input data of

    Hnatyk R., Hnatyk B., Zhdanov V., Voitsekhovskyi V., 2022, MNRAS 516, 4196
    "Unveiling the nature of the unidentified gamma-ray sources
     4FGL J1908.6+0915e, HESS J1907+089/HOTS J1907+091, and
     3HWC J1907+085 in the sky region of the magnetar SGR 1900+14"

------------------------------------------------------------------------
Why this module exists
------------------------------------------------------------------------
For these three sources we do **not** have published per-bin flux points.
What we have instead is, for each instrument, a power-law (PL) fit with an
uncertainty band -- the classic "butterfly".  Following the paper
(see Table 1, footnote: *"Best fit of 20 bins of Fermi-LAT PL 0.05-1000 GeV
spectrum and 20 bins of HOTS PL 1-10 TeV spectrum approximation"*) we turn
each butterfly into a set of synthetic flux points by sampling the PL on a
logarithmic energy grid and attaching a constant *relative* uncertainty
delta_F = rel_err * F (the paper uses rel_err = 0.2).

------------------------------------------------------------------------
Why constant relative error == equal weighting (Goal 2)
------------------------------------------------------------------------
naima fits by minimising chi^2 = sum_i ((model_i - flux_i) / sigma_i)^2.
With sigma_i = rel_err * flux_i, each term becomes
((model_i/flux_i - 1) / rel_err)^2, i.e. a *fractional* residual that does
NOT depend on the absolute flux level.  Combined with a grid that is
uniform in log(E) (equal number of points per decade) this makes every
point -- whether it sits at 100 MeV or at 10 TeV -- carry the SAME weight
in the fit.  Giving each instrument the same number of bins (20 + 20 in the
paper) then makes the two energy bands contribute equally as well.  This is
precisely the "weight all points with the same weight" requirement.

------------------------------------------------------------------------
Standardised table format (naima-native, extensible to any telescope)
------------------------------------------------------------------------
Every spectrum is an astropy QTable saved as ECSV with columns:

    energy           bin centre (geometric mean)         [GeV]
    energy_lo        lower bin edge                       [GeV]
    energy_hi        upper bin edge                       [GeV]
    flux             differential flux dN/dE              [1/(cm2 s GeV)]
    flux_error_lo    lower 1-sigma flux uncertainty       [1/(cm2 s GeV)]
    flux_error_hi    upper 1-sigma flux uncertainty       [1/(cm2 s GeV)]
    ul               upper-limit flag (bool)
    instrument       instrument name (str)
    group            integer instrument id (used by naima)

plus metadata in ``table.meta`` (source name, reference, the PL parameters
used, generation method, confidence level for ULs).  These are exactly the
column names naima's ``validate_data_table`` understands, so the files load
into ``naima.run_sampler`` with no further massaging.

To add a real spectrum from any other telescope you only need to produce a
table with (at minimum) ``energy``, ``flux`` and either ``flux_error`` or
``flux_error_lo``/``flux_error_hi``; use :func:`butterfly_spectrum` for a PL
butterfly or :func:`standardise_points` for genuine flux points.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import astropy.units as u
from astropy.table import QTable, vstack


# Canonical units used throughout (naima is unit-aware, but being explicit
# keeps every file directly comparable and stackable).
ENERGY_UNIT = u.GeV
FLUX_UNIT = u.Unit("1 / (cm2 s GeV)")  # differential flux dN/dE


# =============================================================================
# Published power-law parameters from Hnatyk et al. 2022, Section 2.1
# =============================================================================
# Each entry is a pure power law  dN/dE = norm * (E / pivot)^(-index)
# valid over [energy_min, energy_max].  For H.E.S.S. the normalisation is not
# quoted directly; it is recovered from the integral photon flux above 1 TeV
# (see build_published_spectra()).

PUBLISHED = {
    "fermi": {
        "instrument": "Fermi-LAT",
        "source": "4FGL J1908.6+0915e",
        # F(eps0) = (1.01 +/- 0.19)e-13 ph cm^-2 s^-1 MeV^-1  at eps0 = 4.52 GeV
        "pivot_energy": 4.52 * u.GeV,
        "norm": 1.01e-13 * u.Unit("1 / (cm2 s MeV)"),
        "norm_err": 0.19e-13 * u.Unit("1 / (cm2 s MeV)"),
        "index": 2.23,
        "index_err": 0.098,
        "energy_min": 0.05 * u.GeV,   # 50 MeV
        "energy_max": 1000.0 * u.GeV,  # 1 TeV
        "n_bins": 20,                  # paper: "20 bins of Fermi-LAT PL"
    },
    "hess": {
        "instrument": "H.E.S.S.",
        "source": "HOTS J1907+091",
        # PL approximation: index 2.3 +/- 0.2, delta_F = 0.2 F,
        # normalised to the measured integral flux F(>1 TeV) = 4.3e-13 cm^-2 s^-1.
        "pivot_energy": 1.0 * u.TeV,
        "integral_flux": 4.3e-13 * u.Unit("1 / (cm2 s)"),
        "integral_emin": 1.0 * u.TeV,
        "index": 2.3,
        "index_err": 0.2,
        "energy_min": 1.0 * u.TeV,
        "energy_max": 10.0 * u.TeV,
        "n_bins": 20,                  # paper: "20 bins of HOTS PL"
        # --- for the 'propagated' (bow-tie) error model, baseline dataset ---
        # The paper states delta_F = 0.2 F (no real fit), so we take 20% as the
        # normalisation uncertainty *at the band centre* and let the index error
        # widen it outward.  prop_pivot = geometric centre of the 1-10 TeV band.
        "rel_norm_err": 0.20,
        "prop_pivot": np.sqrt(1.0 * 10.0) * u.TeV,
        "n_bins_baseline": 4,          # ~ real IACT spectral resolution (1 decade)
    },
    "hawc": {
        "instrument": "HAWC",
        "source": "3HWC J1907+085",
        # F(eps0) = (8.4 +0.9 -1.0 (stat) +2.5 -1.62 (sys))e-15 TeV^-1 cm^-2 s^-1
        # at eps0 = 7 TeV, index 2.95 +/- 0.09.  NOTE: in the paper HAWC is
        # over-plotted for comparison, it is NOT part of the fitted dataset.
        "pivot_energy": 7.0 * u.TeV,
        "norm": 8.4e-15 * u.Unit("1 / (cm2 s TeV)"),
        "norm_err": 1.0e-15 * u.Unit("1 / (cm2 s TeV)"),   # stat (larger side)
        "index": 2.95,
        "index_err": 0.09,
        "energy_min": 1.0 * u.TeV,
        "energy_max": 100.0 * u.TeV,
        "n_bins": 20,
        # --- 'propagated' error model: stat+sys normalisation error in quadrature
        # (stat 1.0/8.4 = 0.12, sys 2.5/8.4 = 0.30), index error 0.09, pivot 7 TeV
        "rel_norm_err": float(np.hypot(1.0 / 8.4, 2.5 / 8.4)),  # ~0.32
        "prop_pivot": 7.0 * u.TeV,
        "n_bins_baseline": 6,          # 2 decades
    },
}

REFERENCE = "Hnatyk et al. 2022, MNRAS 516, 4196"

# Integer ids so naima can keep instruments as separate "groups" in a
# combined table (affects nothing in the fit, but keeps plotting/bookkeeping
# clean and lets you mask one instrument easily).
GROUP_ID = {"Fermi-LAT": 0, "H.E.S.S.": 1, "HAWC": 2}


# =============================================================================
# Core builders
# =============================================================================

def _log_bins(energy_min, energy_max, n_bins):
    """Return (e_lo, e_hi, e_centre) for ``n_bins`` log-spaced bins in GeV."""
    emin = energy_min.to_value(ENERGY_UNIT)
    emax = energy_max.to_value(ENERGY_UNIT)
    edges = np.logspace(np.log10(emin), np.log10(emax), n_bins + 1)
    e_lo = edges[:-1] * ENERGY_UNIT
    e_hi = edges[1:] * ENERGY_UNIT
    e_centre = np.sqrt(e_lo * e_hi)  # geometric mean -> centre in log space
    return e_lo, e_hi, e_centre


def power_law(energy, norm, pivot_energy, index):
    """Differential power-law flux dN/dE = norm * (E / pivot)^(-index)."""
    return norm * (energy / pivot_energy) ** (-index)


def norm_from_integral_flux(integral_flux, emin, pivot_energy, index):
    """
    Recover the differential normalisation at ``pivot_energy`` from an integral
    photon flux above ``emin`` for a power law of the given ``index`` (>1):

        F(>emin) = integral_{emin}^{inf} norm (E/pivot)^(-index) dE
                 = norm * pivot / (index - 1) * (emin/pivot)^(1-index)
    =>  norm     = F(>emin) * (index - 1) / pivot * (emin/pivot)^(index-1)
    """
    norm = (
        integral_flux
        * (index - 1)
        / pivot_energy
        * (emin / pivot_energy) ** (index - 1)
    )
    return norm.to(FLUX_UNIT)


def standardise_points(energy, flux, flux_error_lo, flux_error_hi,
                       energy_lo, energy_hi, instrument, source,
                       ul=None, cl=0.95, **meta):
    """
    Assemble a standardised, naima-ready QTable from arrays of points.

    Use this to inject *real* flux points from any other telescope: just pass
    the per-bin energies, fluxes and (a)symmetric errors.  All array arguments
    must be astropy Quantities with compatible units.
    """
    energy = energy.to(ENERGY_UNIT)
    n = len(energy)
    if ul is None:
        ul = np.zeros(n, dtype=bool)

    t = QTable()
    t["energy"] = energy
    t["energy_lo"] = energy_lo.to(ENERGY_UNIT)
    t["energy_hi"] = energy_hi.to(ENERGY_UNIT)
    t["flux"] = flux.to(FLUX_UNIT)
    t["flux_error_lo"] = flux_error_lo.to(FLUX_UNIT)
    t["flux_error_hi"] = flux_error_hi.to(FLUX_UNIT)
    t["ul"] = np.asarray(ul, dtype=bool)
    t["instrument"] = [instrument] * n
    t["group"] = [GROUP_ID.get(instrument, 0)] * n

    # naima reads the upper-limit confidence level from meta["keywords"]["cl"]
    t.meta["keywords"] = {"cl": {"value": cl}}
    t.meta["instrument"] = instrument
    t.meta["source"] = source
    t.meta["reference"] = REFERENCE
    t.meta.update(meta)
    return t


def butterfly_spectrum(params, error_model="flat", rel_err=0.2, n_bins=None):
    """
    Build a standardised spectrum by sampling a published power-law butterfly.

    Parameters
    ----------
    params : dict
        One entry of :data:`PUBLISHED` (or any dict with the same keys).
    error_model : {"flat", "propagated"}
        How the per-point 1-sigma flux error is set:

        - ``"flat"``  : constant relative error, delta_F = ``rel_err`` * F.
          This is the equal-weight construction of Hnatyk et al. 2022 (every
          point weighs the same). Simple but ignores the real uncertainty shape.
        - ``"propagated"`` : a proper *bow-tie*. The error grows away from the
          decorrelation/pivot energy following the power-law fit covariance,
          delta_F/F = sqrt( (sigma_N0/N0)^2 + (ln(E/E_pivot) * sigma_Gamma)^2 ).
          Uses ``params["rel_norm_err"]``, ``params["index_err"]`` and
          ``params["prop_pivot"]``. More faithful; used for the baseline dataset.
    rel_err : float
        Relative error for ``error_model="flat"`` (default 0.2).
    n_bins : int, optional
        Number of log-spaced bins. Defaults to ``params["n_bins"]`` for the flat
        model and ``params["n_bins_baseline"]`` for the propagated model.

    Returns
    -------
    QTable
        Standardised, naima-ready spectrum.
    """
    if n_bins is None:
        n_bins = params["n_bins_baseline"] if error_model == "propagated" else params["n_bins"]
    e_lo, e_hi, energy = _log_bins(params["energy_min"], params["energy_max"], n_bins)

    # Normalisation: quoted directly, or recovered from an integral flux.
    if "norm" in params:
        norm = params["norm"]
    else:
        norm = norm_from_integral_flux(
            params["integral_flux"], params["integral_emin"],
            params["pivot_energy"], params["index"],
        )

    flux = power_law(energy, norm, params["pivot_energy"], params["index"]).to(FLUX_UNIT)

    if error_model == "flat":
        rel = np.full(len(energy), rel_err)
        gen = f"butterfly: flat {rel_err:.0%} relative error (equal weight)"
    elif error_model == "propagated":
        lnE = np.log((energy / params["prop_pivot"]).to_value(u.dimensionless_unscaled))
        rel = np.sqrt(params["rel_norm_err"] ** 2 + (lnE * params["index_err"]) ** 2)
        gen = "butterfly: error propagated from PL norm+index covariance (bow-tie)"
    else:
        raise ValueError(f"unknown error_model {error_model!r}")

    dflux = (rel * flux).to(FLUX_UNIT)

    return standardise_points(
        energy=energy, flux=flux,
        flux_error_lo=dflux, flux_error_hi=dflux,
        energy_lo=e_lo, energy_hi=e_hi,
        instrument=params["instrument"], source=params["source"],
        pivot_energy=str(params["pivot_energy"]),
        index=params["index"],
        error_model=error_model,
        generation=gen,
    )


def load_fermi_catalog(filepath, source="4FGL J1908.6+0915e", cl=0.95):
    """
    Load the **real** Fermi-LAT SED points from a fermipy flux-point table
    (the ``FERMI_CATALOG.txt`` produced by the likelihood analysis) into the
    standardised format.

    The table carries ``e2dnde = E^2 dN/dE`` [erg/cm2/s] with asymmetric errors
    and upper-limit flags; we convert to differential flux dN/dE and mark the
    upper-limit bins so naima treats them with its upper-limit likelihood.

    Parameters
    ----------
    filepath : str or Path
    source : str
        Source name stored in the metadata.
    cl : float
        Confidence level of the upper limits (fermipy default 0.95).
    """
    from astropy.table import Table

    t = Table.read(str(filepath), format="ascii.fixed_width_two_line",
                   header_start=0, position_line=2, data_start=3)

    e_lo = np.array(t["e_min"]) * u.MeV
    e_hi = np.array(t["e_max"]) * u.MeV
    energy = np.sqrt(e_lo * e_hi)

    ul = np.array([str(x) == "True" for x in t["is_ul"]])
    e2 = u.Unit("erg / (cm2 s)")
    e2dnde = np.array(t["e2dnde"]) * e2
    e2dnde_errn = np.nan_to_num(np.array(t["e2dnde_errn"], dtype=float)) * e2
    e2dnde_errp = np.nan_to_num(np.array(t["e2dnde_errp"], dtype=float)) * e2
    e2dnde_ul = np.nan_to_num(np.array(t["e2dnde_ul"], dtype=float)) * e2

    # E^2 dN/dE  ->  dN/dE
    flux = (e2dnde / energy**2).to(FLUX_UNIT)
    err_lo = (e2dnde_errn / energy**2).to(FLUX_UNIT)
    err_hi = (e2dnde_errp / energy**2).to(FLUX_UNIT)

    # For UL bins, store the limit as the "flux" (naima reads it as the limit)
    # and give it a nominal error so the column is finite.
    ul_flux = (e2dnde_ul / energy**2).to(FLUX_UNIT)
    flux = np.where(ul, ul_flux.value, flux.value) * FLUX_UNIT
    err_lo = np.where(ul, 0.5 * ul_flux.value, err_lo.value) * FLUX_UNIT
    err_hi = np.where(ul, 0.5 * ul_flux.value, err_hi.value) * FLUX_UNIT

    return standardise_points(
        energy=energy, flux=flux, flux_error_lo=err_lo, flux_error_hi=err_hi,
        energy_lo=e_lo, energy_hi=e_hi,
        instrument="Fermi-LAT", source=source, ul=ul, cl=cl,
        generation="real fermipy SED points (FERMI_CATALOG.txt)",
    )


def combine_spectra(*tables):
    """Vertically stack standardised spectra into one table, sorted by energy."""
    combined = vstack(list(tables), metadata_conflicts="silent")
    combined.sort("energy")
    combined.meta["instrument"] = "+".join(
        dict.fromkeys(t.meta.get("instrument", "?") for t in tables)
    )
    combined.meta["reference"] = REFERENCE
    # keep a single, consistent cl keyword for naima
    combined.meta["keywords"] = {"cl": {"value": 0.95}}
    return combined


# =============================================================================
# I/O
# =============================================================================

def save_spectrum(table, filepath):
    """Write a standardised spectrum to ECSV (self-describing, unit-aware)."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    table.write(filepath, format="ascii.ecsv", overwrite=True)
    return filepath


def load_spectrum(filepath):
    """Read a standardised spectrum ECSV back into a QTable."""
    return QTable.read(filepath, format="ascii.ecsv")


# =============================================================================
# Driver: regenerate all standardised files in spectra/
# =============================================================================

def build_published_spectra(outdir=None, fermi_catalog=None):
    """
    Generate the standardised spectrum files and write them to ``outdir``
    (default: ./spectra). Two parallel datasets are produced:

    **Baseline (scientific default): real Fermi + propagated TeV.**
        - real Fermi-LAT SED points (from ``fermi_catalog``; includes upper limits)
        - H.E.S.S. / HAWC sampled sparsely with bow-tie (propagated) errors
        Inverse-variance weighting with realistic errors.

    **Cross-check (paper reproduction): flat 0.2 F equal weighting.**
        - 20 + 20 log-spaced points per instrument, constant 20% error.

    Returns a dict mapping a short key to the written file path.
    """
    outdir = Path(outdir) if outdir else Path(__file__).parent / "spectra"
    if fermi_catalog is None:
        fermi_catalog = Path(__file__).parent / "FERMI_CATALOG.txt"
    fermi_catalog = Path(fermi_catalog)

    paths = {}

    # ---- Baseline: real Fermi + propagated (bow-tie) TeV ------------------
    # This is the ONLY part that needs an external input file (the real Fermi
    # SED). If it is missing we simply skip the real-Fermi products and still
    # build everything that comes from the published power-law parameters.
    hess_prop = butterfly_spectrum(PUBLISHED["hess"], error_model="propagated")
    hawc_prop = butterfly_spectrum(PUBLISHED["hawc"], error_model="propagated")
    paths["hess_prop"] = save_spectrum(hess_prop, outdir / "hess_hots_propagated.ecsv")
    paths["hawc_prop"] = save_spectrum(hawc_prop, outdir / "hawc_3hwc_propagated.ecsv")

    if fermi_catalog.exists():
        fermi_real = load_fermi_catalog(fermi_catalog)
        baseline = combine_spectra(fermi_real, hess_prop)
        baseline_hawc = combine_spectra(fermi_real, hess_prop, hawc_prop)
        paths["fermi_real"] = save_spectrum(fermi_real, outdir / "fermi_real_4fgl.ecsv")
        paths["baseline"] = save_spectrum(baseline, outdir / "combined_real_baseline.ecsv")
        paths["baseline_hawc"] = save_spectrum(baseline_hawc, outdir / "combined_real_baseline_hawc.ecsv")
    else:
        print(f"NOTE: {fermi_catalog.name} not found -> skipping the real-Fermi "
              "baseline dataset (combined_real_baseline*.ecsv). The butterfly / "
              "flat datasets below need no input file. Provide the catalog, or "
              "point the notebooks at 'combined_fermi_hess.ecsv' instead.")

    # ---- Cross-check: paper's flat 0.2 F equal-weight construction --------
    # Built entirely from the published power-law parameters -- no input file.
    fermi_flat = butterfly_spectrum(PUBLISHED["fermi"], error_model="flat")
    hess_flat = butterfly_spectrum(PUBLISHED["hess"], error_model="flat")
    hawc_flat = butterfly_spectrum(PUBLISHED["hawc"], error_model="flat")
    flat_fermi_hess = combine_spectra(fermi_flat, hess_flat)
    flat_fermi_hess_hawc = combine_spectra(fermi_flat, hess_flat, hawc_flat)
    paths["fermi_flat"] = save_spectrum(fermi_flat, outdir / "fermi_4fgl_j1908.ecsv")
    paths["hess_flat"] = save_spectrum(hess_flat, outdir / "hess_hots_j1907.ecsv")
    paths["hawc_flat"] = save_spectrum(hawc_flat, outdir / "hawc_3hwc_j1907.ecsv")
    paths["flat_fermi_hess"] = save_spectrum(flat_fermi_hess, outdir / "combined_fermi_hess.ecsv")
    paths["flat_fermi_hess_hawc"] = save_spectrum(flat_fermi_hess_hawc, outdir / "combined_fermi_hess_hawc.ecsv")

    return paths


if __name__ == "__main__":
    paths = build_published_spectra()
    print("Standardised spectra written to spectra/ :")
    print("\n[baseline: real Fermi + propagated TeV]")
    for key in ["fermi_real", "hess_prop", "hawc_prop", "baseline", "baseline_hawc"]:
        if key not in paths:
            continue
        t = load_spectrum(paths[key])
        n_ul = int(np.sum(t["ul"])) if "ul" in t.colnames else 0
        print(f"  {key:14s} -> {paths[key].name:34s} "
              f"({len(t):2d} pts, {n_ul} ULs, {t['energy'].min():.3g}-{t['energy'].max():.3g})")
    print("\n[cross-check: paper flat 0.2 F equal weighting]")
    for key in ["fermi_flat", "hess_flat", "hawc_flat", "flat_fermi_hess", "flat_fermi_hess_hawc"]:
        t = load_spectrum(paths[key])
        n_ul = int(np.sum(t["ul"])) if "ul" in t.colnames else 0
        print(f"  {key:14s} -> {paths[key].name:34s} "
              f"({len(t):2d} pts, {n_ul} ULs, {t['energy'].min():.3g}-{t['energy'].max():.3g})")
