"""
Spectrum Builder for Naima Fitting

This module builds combined gamma-ray spectra from Fermi-LAT, H.E.S.S., and HAWC data
following the methodology from Hnatyk et al. 2022 (MNRAS).

The spectrum points are generated using the published spectral parameters and can be
combined with actual Fermi-LAT measurements when available.

Reference: Hnatyk et al. 2022, MNRAS, "Unveiling the nature of the unidentified
gamma-ray sources 4FGL J1908.6+0915e, HESS J1907+089/HOTS J1907+091, and
3HWC J1907+085 in the sky region of the magnetar SGR 1900+14"
"""

import numpy as np
import astropy.units as u
from astropy.table import QTable
from pathlib import Path


# =============================================================================
# Published Spectral Parameters from Hnatyk et al. 2022
# =============================================================================

# Fermi-LAT 4FGL J1908.6+0915e (Section 2.1)
FERMI_PARAMS = {
    'pivot_energy': 4.52 * u.GeV,
    'norm': 1.01e-13 * u.Unit('ph cm-2 s-1 MeV-1'),  # at pivot energy
    'norm_err': 0.19e-13 * u.Unit('ph cm-2 s-1 MeV-1'),
    'index': 2.23,
    'index_err': 0.098,
    'energy_min': 0.05 * u.GeV,  # 50 MeV
    'energy_max': 1000 * u.GeV,  # 1 TeV
}

# H.E.S.S. HOTS J1907+091 / HESS J1907+089 (Section 2.1)
# Approximated power-law based on Fermi-LAT extension
HESS_PARAMS = {
    'integral_flux_above_1TeV': 4.3e-13 * u.Unit('cm-2 s-1'),
    'index': 2.3,
    'index_err': 0.2,
    'energy_min': 1.0 * u.TeV,
    'energy_max': 10.0 * u.TeV,
}

# HAWC 3HWC J1907+085 (Section 2.1)
HAWC_PARAMS = {
    'pivot_energy': 7.0 * u.TeV,
    'norm': 8.4e-15 * u.Unit('TeV-1 cm-2 s-1'),
    'norm_err_lo': 1.0e-15 * u.Unit('TeV-1 cm-2 s-1'),
    'norm_err_hi': 0.9e-15 * u.Unit('TeV-1 cm-2 s-1'),
    'norm_sys_lo': 1.62e-15 * u.Unit('TeV-1 cm-2 s-1'),
    'norm_sys_hi': 2.5e-15 * u.Unit('TeV-1 cm-2 s-1'),
    'index': 2.95,
    'index_err': 0.09,
    'energy_min': 1.0 * u.TeV,
    'energy_max': 100.0 * u.TeV,
}


def power_law_flux(energy, norm, pivot_energy, index):
    """
    Power-law differential flux: dN/dE = N0 * (E/E0)^(-Γ)

    Parameters
    ----------
    energy : Quantity
        Photon energies
    norm : Quantity
        Normalization at pivot energy [1/(cm² s energy_unit)]
    pivot_energy : Quantity
        Pivot/reference energy
    index : float
        Photon spectral index (positive)

    Returns
    -------
    flux : Quantity
        Differential flux at given energies
    """
    return norm * (energy / pivot_energy) ** (-index)


def generate_fermi_spectrum(energy_min=0.2*u.GeV, energy_max=1000*u.GeV,
                            n_bins=10, log_spacing=True):
    """
    Generate Fermi-LAT spectrum points based on published power-law parameters.

    Parameters
    ----------
    energy_min : Quantity
        Minimum energy (default 200 MeV as requested)
    energy_max : Quantity
        Maximum energy (default 1 TeV)
    n_bins : int
        Number of energy bins
    log_spacing : bool
        Use logarithmic energy spacing

    Returns
    -------
    table : QTable
        Spectrum table with columns: energy, energy_edge_lo, energy_edge_hi,
        flux, flux_error
    """
    if log_spacing:
        e_lo = np.logspace(np.log10(energy_min.to(u.GeV).value),
                           np.log10(energy_max.to(u.GeV).value),
                           n_bins + 1)[:-1] * u.GeV
        e_hi = np.logspace(np.log10(energy_min.to(u.GeV).value),
                           np.log10(energy_max.to(u.GeV).value),
                           n_bins + 1)[1:] * u.GeV
    else:
        e_lo = np.linspace(energy_min.to(u.GeV).value,
                           energy_max.to(u.GeV).value,
                           n_bins + 1)[:-1] * u.GeV
        e_hi = np.linspace(energy_min.to(u.GeV).value,
                           energy_max.to(u.GeV).value,
                           n_bins + 1)[1:] * u.GeV

    # Geometric mean for bin center
    energy = np.sqrt(e_lo * e_hi)

    # Calculate flux at bin centers
    norm_gev = FERMI_PARAMS['norm'].to(u.Unit('1/(cm2 s GeV)'))
    norm_err_gev = FERMI_PARAMS['norm_err'].to(u.Unit('1/(cm2 s GeV)'))
    pivot = FERMI_PARAMS['pivot_energy']
    index = FERMI_PARAMS['index']

    flux = power_law_flux(energy, norm_gev, pivot, index)

    # Error propagation (simplified - dominated by normalization uncertainty)
    # Relative error ~ sqrt((dN/N)^2 + (dΓ * ln(E/E0))^2)
    rel_norm_err = (norm_err_gev / norm_gev).decompose().value
    rel_index_err = FERMI_PARAMS['index_err'] * np.abs(np.log((energy / pivot).decompose().value))
    rel_err = np.sqrt(rel_norm_err**2 + rel_index_err**2)
    flux_error = flux * rel_err

    # Assume 20% systematic floor as in paper
    flux_error = np.maximum(flux_error, 0.2 * flux)

    table = QTable()
    table['energy'] = energy
    table['energy_edge_lo'] = e_lo
    table['energy_edge_hi'] = e_hi
    table['flux'] = flux
    table['flux_error'] = flux_error
    table.meta['instrument'] = 'Fermi-LAT'
    table.meta['source'] = '4FGL J1908.6+0915e'

    return table


def generate_hess_spectrum(energy_min=1.0*u.TeV, energy_max=10.0*u.TeV, n_bins=10):
    """
    Generate H.E.S.S. spectrum points based on published parameters.

    The spectrum is approximated as power-law with index ~2.3 and normalized
    to match the integral flux above 1 TeV.
    """
    e_lo = np.logspace(np.log10(energy_min.to(u.TeV).value),
                       np.log10(energy_max.to(u.TeV).value),
                       n_bins + 1)[:-1] * u.TeV
    e_hi = np.logspace(np.log10(energy_min.to(u.TeV).value),
                       np.log10(energy_max.to(u.TeV).value),
                       n_bins + 1)[1:] * u.TeV

    energy = np.sqrt(e_lo * e_hi)

    # Derive normalization from integral flux
    # ∫_{E_min}^{∞} N0*(E/E0)^{-Γ} dE = F_int
    # For Γ > 1: F_int = N0 * E0 / (Γ-1) * (E_min/E0)^{1-Γ}
    # => N0 = F_int * (Γ-1) / E0 * (E_min/E0)^{Γ-1}
    index = HESS_PARAMS['index']
    E0 = 1.0 * u.TeV  # pivot energy
    E_min_int = 1.0 * u.TeV
    F_int = HESS_PARAMS['integral_flux_above_1TeV']

    norm = F_int * (index - 1) / E0 * (E_min_int / E0) ** (index - 1)
    norm = norm.to(u.Unit('1/(cm2 s TeV)'))

    flux = power_law_flux(energy, norm, E0, index)
    flux = flux.to(u.Unit('1/(cm2 s GeV)'))

    # 20% relative error as standard deviation (as in paper δF = 0.2F)
    flux_error = 0.2 * flux

    table = QTable()
    table['energy'] = energy.to(u.GeV)
    table['energy_edge_lo'] = e_lo.to(u.GeV)
    table['energy_edge_hi'] = e_hi.to(u.GeV)
    table['flux'] = flux
    table['flux_error'] = flux_error
    table.meta['instrument'] = 'H.E.S.S.'
    table.meta['source'] = 'HOTS J1907+091'

    return table


def generate_hawc_spectrum(energy_min=1.0*u.TeV, energy_max=100.0*u.TeV, n_bins=5):
    """
    Generate HAWC spectrum points based on published parameters.
    """
    e_lo = np.logspace(np.log10(energy_min.to(u.TeV).value),
                       np.log10(energy_max.to(u.TeV).value),
                       n_bins + 1)[:-1] * u.TeV
    e_hi = np.logspace(np.log10(energy_min.to(u.TeV).value),
                       np.log10(energy_max.to(u.TeV).value),
                       n_bins + 1)[1:] * u.TeV

    energy = np.sqrt(e_lo * e_hi)

    norm = HAWC_PARAMS['norm'].to(u.Unit('1/(cm2 s TeV)'))
    pivot = HAWC_PARAMS['pivot_energy']
    index = HAWC_PARAMS['index']

    flux = power_law_flux(energy, norm, pivot, index)
    flux = flux.to(u.Unit('1/(cm2 s GeV)'))

    # Combined statistical and systematic errors
    rel_stat = 0.12  # ~12% from stat errors
    rel_sys = 0.20   # ~20% systematic
    rel_err = np.sqrt(rel_stat**2 + rel_sys**2)
    flux_error = rel_err * flux

    table = QTable()
    table['energy'] = energy.to(u.GeV)
    table['energy_edge_lo'] = e_lo.to(u.GeV)
    table['energy_edge_hi'] = e_hi.to(u.GeV)
    table['flux'] = flux
    table['flux_error'] = flux_error
    table.meta['instrument'] = 'HAWC'
    table.meta['source'] = '3HWC J1907+085'

    return table


def combine_spectra(fermi_table, hess_table, hawc_table=None,
                    use_hawc=False, energy_min=0.2*u.GeV):
    """
    Combine Fermi-LAT, H.E.S.S., and optionally HAWC spectra into a single table.

    Parameters
    ----------
    fermi_table : QTable
        Fermi-LAT spectrum
    hess_table : QTable
        H.E.S.S. spectrum
    hawc_table : QTable, optional
        HAWC spectrum
    use_hawc : bool
        Include HAWC data (default False - as in paper's main analysis)
    energy_min : Quantity
        Minimum energy threshold

    Returns
    -------
    combined : QTable
        Combined spectrum table suitable for naima fitting
    """
    from astropy.table import vstack

    # Filter by energy minimum
    mask_fermi = fermi_table['energy'] >= energy_min
    mask_hess = hess_table['energy'] >= energy_min

    tables = [fermi_table[mask_fermi], hess_table[mask_hess]]

    if use_hawc and hawc_table is not None:
        mask_hawc = hawc_table['energy'] >= energy_min
        tables.append(hawc_table[mask_hawc])

    combined = vstack(tables)

    # Sort by energy
    combined.sort('energy')

    # Add metadata
    combined.meta['cl'] = 0.68  # 1-sigma confidence level
    combined.meta['energy_min'] = energy_min

    return combined


def load_fermi_from_file(filepath):
    """
    Load Fermi-LAT spectrum points from a text file.

    Expected format (space/tab separated):
    energy[GeV]  energy_edge_lo[GeV]  energy_edge_hi[GeV]  flux[1/(cm2 s GeV)]  flux_error[1/(cm2 s GeV)]

    Parameters
    ----------
    filepath : str or Path
        Path to the spectrum file

    Returns
    -------
    table : QTable
        Spectrum table
    """
    filepath = Path(filepath)

    data = np.loadtxt(filepath, comments='#')

    if data.shape[1] >= 5:
        table = QTable()
        table['energy'] = data[:, 0] * u.GeV
        table['energy_edge_lo'] = data[:, 1] * u.GeV
        table['energy_edge_hi'] = data[:, 2] * u.GeV
        table['flux'] = data[:, 3] * u.Unit('1/(cm2 s GeV)')
        table['flux_error'] = data[:, 4] * u.Unit('1/(cm2 s GeV)')
    elif data.shape[1] >= 3:
        # Simplified format: energy, flux, flux_error
        table = QTable()
        table['energy'] = data[:, 0] * u.GeV
        table['flux'] = data[:, 1] * u.Unit('1/(cm2 s GeV)')
        table['flux_error'] = data[:, 2] * u.Unit('1/(cm2 s GeV)')
        # Estimate bin edges (factor of sqrt(2) half-width in log space)
        table['energy_edge_lo'] = table['energy'] / np.sqrt(2)
        table['energy_edge_hi'] = table['energy'] * np.sqrt(2)
    else:
        raise ValueError(f"Unexpected data format in {filepath}")

    table.meta['instrument'] = 'Fermi-LAT'
    table.meta['source_file'] = str(filepath)

    return table


def build_spectrum_for_naima(fermi_file=None, energy_min=0.2*u.GeV,
                             n_fermi_bins=10, n_hess_bins=10, n_hawc_bins=5,
                             use_hawc=False):
    """
    Build a complete spectrum for naima fitting.

    If fermi_file is provided, use actual Fermi data. Otherwise, generate
    synthetic spectrum from published parameters.

    Parameters
    ----------
    fermi_file : str or Path, optional
        Path to Fermi-LAT spectrum file
    energy_min : Quantity
        Minimum energy (default 200 MeV)
    n_fermi_bins : int
        Number of Fermi energy bins (if generating)
    n_hess_bins : int
        Number of H.E.S.S. energy bins
    n_hawc_bins : int
        Number of HAWC energy bins
    use_hawc : bool
        Include HAWC data

    Returns
    -------
    spectrum : QTable
        Combined spectrum ready for naima fitting
    """
    # Fermi spectrum
    if fermi_file is not None:
        fermi = load_fermi_from_file(fermi_file)
    else:
        fermi = generate_fermi_spectrum(
            energy_min=energy_min,
            energy_max=1000*u.GeV,
            n_bins=n_fermi_bins
        )

    # H.E.S.S. spectrum
    hess = generate_hess_spectrum(
        energy_min=1.0*u.TeV,
        energy_max=10.0*u.TeV,
        n_bins=n_hess_bins
    )

    # HAWC spectrum
    hawc = None
    if use_hawc:
        hawc = generate_hawc_spectrum(
            energy_min=1.0*u.TeV,
            energy_max=100.0*u.TeV,
            n_bins=n_hawc_bins
        )

    # Combine
    spectrum = combine_spectra(fermi, hess, hawc, use_hawc=use_hawc,
                               energy_min=energy_min)

    return spectrum


def save_spectrum(spectrum, filepath, format='ascii.ecsv'):
    """
    Save spectrum table to file.

    Parameters
    ----------
    spectrum : QTable
        Spectrum table
    filepath : str or Path
        Output file path
    format : str
        Astropy table format (default 'ascii.ecsv')
    """
    filepath = Path(filepath)
    spectrum.write(filepath, format=format, overwrite=True)
    print(f"Saved spectrum to {filepath}")


# =============================================================================
# Main execution
# =============================================================================

if __name__ == "__main__":
    # Example: Generate combined Fermi+H.E.S.S. spectrum
    print("Building combined Fermi-LAT + H.E.S.S. spectrum...")

    spectrum = build_spectrum_for_naima(
        fermi_file=None,  # Use synthetic Fermi data
        energy_min=0.2*u.GeV,
        n_fermi_bins=10,
        n_hess_bins=10,
        use_hawc=False
    )

    print("\nCombined Spectrum:")
    print(spectrum)

    # Save to file
    output_dir = Path(__file__).parent / "spectra"
    output_dir.mkdir(exist_ok=True)
    save_spectrum(spectrum, output_dir / "combined_fermi_hess_spectrum.ecsv")
