import marimo

__generated_with = "0.13.6"
app = marimo.App()


@app.cell
def _():
    from astropy import units as u
    import matplotlib.pyplot as plt

    def fermi_lat_psf_quantity(E):
        """
        Like fermi_lat_psf, but takes/returns an Astropy Quantity.

        Parameters
        ----------
        E : astropy.units.Quantity
            Photon energy (e.g. in MeV or GeV).

        Returns
        -------
        psf : astropy.units.Quantity
            PSF in degrees.
        """
        E = E.to(u.MeV)
        psf = 3.5 * (E / (100 * u.MeV))**(-0.8) * u.deg
        return psf

    # Example with units
    if __name__ == "__main__":
        Eq = [50, 100, 1000, 5000, 10000, 50000, 100000, 200000] * u.MeV
        psf_values = fermi_lat_psf_quantity(Eq)
        for e in Eq:
            print(f"Energy: {e}, PSF: {fermi_lat_psf_quantity(e)}")
        #
    return Eq, plt, psf_values


@app.cell
def _(Eq, plt, psf_values):
    from matplotlib.ticker import ScalarFormatter

    plt.figure(figsize=(9, 7))    
    plt.plot(Eq, psf_values)

    plt.xlabel("Energy (MeV)")
    plt.ylabel("PSF (degrees)")

    plt.xscale("log")
    plt.ylim(0,0.6)
    plt.xlim(1000,200000)
    plt.gca().yaxis.set_major_formatter(ScalarFormatter())
    plt.gca().yaxis.get_major_formatter().set_scientific(False)
    return


@app.cell
def _():
    from astropy.io import fits

    def _load_psf_quartile_tables(fits_path, memmap=True):
        """
        Load RPSF, scaling params, and fisheye tables for PSF0–PSF3.

        Parameters
        ----------
        fits_path : str
            Path to 'psf_P8R3_SOURCE_V3_PSF.fits' (local or URL).
        memmap : bool
            Whether to memory-map the file (saves RAM on large tables).

        Returns
        -------
        psf_tables : dict
            A dict keyed by quartile string 'PSF0'...'PSF3', each mapping to a
            sub-dict with keys 'rpsf', 'scale', 'fisheye' holding the HDU.data
            structured arrays.
        """
        hdul = fits.open(fits_path, memmap=memmap)
        psf_tables = {}
        for q in range(4):
            key = f'PSF{q}'
            rpsf_name = f'RPSF_PSF{q}'
            scale_name = f'PSF_SCALING_PARAMS_PSF{q}'
            fisheye_name = f'FISHEYE_CORRECTION_PSF{q}'
            rpsf_hdu = hdul[rpsf_name]
            scale_hdu = hdul[scale_name]
            fisheye_hdu = hdul[fisheye_name]
            psf_tables[key] = {'rpsf': rpsf_hdu.data, 'scale': scale_hdu.data, 'fisheye': fisheye_hdu.data}
        hdul.close()
        return psf_tables
    if __name__ == '__main__':
        _fits_file = '/Users/vdk/miniforge3/envs/fermipy/share/fermitools/data/caldb/data/glast/lat/bcf/psf/psf_P8R3_SOURCE_V3_PSF.fits'
        tables = _load_psf_quartile_tables(_fits_file)
    return (fits,)


@app.cell
def _(fits):
    _fits_file = '/Users/vdk/miniforge3/envs/fermipy/share/fermitools/data/caldb/data/glast/lat/bcf/psf/psf_P8R3_SOURCE_V3_PSF.fits'
    with fits.open(_fits_file) as hdu:
        print(hdu.info())
    return


@app.cell
def _(fits_1, u_1):
    import os
    from astropy.io import fits
    import numpy as np
    import astropy.units as u

    def _load_psf_quartile_tables(irf_fits_path):
        """
        Read the PSF FITS file and return a dict of quartile tables:
          {
            'PSF0': {'rpsf': ..., 'scale': ..., 'fisheye': ...},
            'PSF1': { … },
            ...
          }
        """
        hdul = fits_1.open(irf_fits_path)
        quartiles = {}
        for q in range(4):
            tag = f'PSF{q}'
            rpsf = hdul[f'RPSF_{tag}'].data
            scale = hdul[f'PSF_SCALING_PARAMS_{tag}'].data
            fisheye = hdul[f'FISHEYE_CORRECTION_{tag}'].data
            quartiles[tag] = {'rpsf': rpsf, 'scale': scale, 'fisheye': fisheye}
        hdul.close()
        return quartiles

    def load_psf_params_from_scaling(irf_fits_path, quartile):
        """
        Return the c0, c1, beta parameters for the given PSF quartile.
    
        Parameters
        ----------
        irf_fits_path : str
            Path to the PSF FITS (e.g. psf_P8R3_SOURCE_V3_PSF.fits).
        quartile : str
            One of 'PSF0', 'PSF1', 'PSF2', 'PSF3'.
    
        Returns
        -------
        c0, c1, beta : astropy.Quantity, astropy.Quantity, float
        """
        tables = _load_psf_quartile_tables(irf_fits_path)
        if quartile not in tables:
            raise ValueError(f"Invalid quartile '{quartile}'; must be PSF0–PSF3")
        psf_scale = tables[quartile]['scale']['PSFSCALE'][0]
        c0 = psf_scale[0] * u_1.rad
        c1 = psf_scale[1] * u_1.rad
        beta = float(psf_scale[2])
        return (c0, c1, beta)

    def compute_r68(energy, c0, c1, beta, e0=100 * u_1.MeV):
        """
        Compute R68 = sqrt[ (c0*(E/E0)^(-beta))^2 + c1^2 ].
        """
        E = energy.to(e0.unit)
        core = c0 * (E / e0) ** beta
        return np.sqrt(core ** 2 + c1 ** 2)
    return compute_r68, fits, load_psf_params_from_scaling, np


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### PSF0
        """
    )
    return


@app.cell
def _(compute_r68, load_psf_params_from_scaling, np, u_1):
    psf_params = load_psf_params_from_scaling('/Users/vdk/miniforge3/envs/fermipy/share/fermitools/data/caldb/data/glast/lat/bcf/psf/psf_P8R3_SOURCE_V3_PSF.fits', 'PSF0')
    np.rad2deg(compute_r68(3000 * u_1.MeV, psf_params[0], psf_params[1], psf_params[2]))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### PSF1
        """
    )
    return


@app.cell
def _(compute_r68, load_psf_params_from_scaling, np, u_1):
    psf_params_1 = load_psf_params_from_scaling('/Users/vdk/miniforge3/envs/fermipy/share/fermitools/data/caldb/data/glast/lat/bcf/psf/psf_P8R3_SOURCE_V3_PSF.fits', 'PSF1')
    np.rad2deg(compute_r68(3000 * u_1.MeV, psf_params_1[0], psf_params_1[1], psf_params_1[2]))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### PSF2
        """
    )
    return


@app.cell
def _(compute_r68, load_psf_params_from_scaling, np, u_1):
    psf_params_2 = load_psf_params_from_scaling('/Users/vdk/miniforge3/envs/fermipy/share/fermitools/data/caldb/data/glast/lat/bcf/psf/psf_P8R3_SOURCE_V3_PSF.fits', 'PSF2')
    np.rad2deg(compute_r68(3000 * u_1.MeV, psf_params_2[0], psf_params_2[1], psf_params_2[2]))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### PSF3
        """
    )
    return


@app.cell
def _(compute_r68, load_psf_params_from_scaling, np, u_1):
    psf_params_3 = load_psf_params_from_scaling('/Users/vdk/miniforge3/envs/fermipy/share/fermitools/data/caldb/data/glast/lat/bcf/psf/psf_P8R3_SOURCE_V3_PSF.fits', 'PSF3')
    np.rad2deg(compute_r68(3000 * u_1.MeV, psf_params_3[0], psf_params_3[1], psf_params_3[2]))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### PSF for FRONT events
        """
    )
    return


@app.cell
def _(compute_r68, np, u_1):
    np.rad2deg(compute_r68(1000 * u_1.MeV, 0.0638 * u_1.rad, 0.00126 * u_1.rad, -0.8))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### PSF for BACK events
        """
    )
    return


@app.cell
def _(compute_r68, np, u_1):
    np.rad2deg(compute_r68(1000 * u_1.MeV, 0.123 * u_1.rad, 0.00222 * u_1.rad, -0.8))
    return


@app.cell
def _(compute_r68, load_psf_params_from_scaling, np, u_1):
    psf_params_4 = load_psf_params_from_scaling('/Users/vdk/miniforge3/envs/fermipy/share/fermitools/data/caldb/data/glast/lat/bcf/psf/psf_P8R3_SOURCE_V3_PSF.fits', 'PSF0')
    np.rad2deg(compute_r68(1000 * u_1.MeV, np.rad2deg(psf_params_4[0]), np.rad2deg(psf_params_4[1]), psf_params_4[2]))
    return (psf_params_4,)


@app.cell
def _(fits_1, u_1):
    def read_psf_scale_coeffs(fits_file, psf_quartile):
        """
        Read the PSFSCALE coefficients (c0, c1, beta) for a given PSF quartile
        from the P8R3_SOURCE_V3 PSF FITS file, converting the angular terms
        from radians into degrees.

        Parameters
        ----------
        fits_file : str
            Path to the PSF FITS file (e.g. 'psf_P8R3_SOURCE_V3_PSF.fits').
        psf_quartile : str
            One of 'PSF0', 'PSF1', 'PSF2', 'PSF3'.

        Returns
        -------
        c0_deg : astropy.units.Quantity
            Core scale at reference energy, in degrees.
        c1_deg : astropy.units.Quantity
            Asymptotic tail floor, in degrees.
        beta : float
            Power-law index.
        """
        with fits_1.open(_fits_file) as hdul:
            extname = f'PSF_SCALING_PARAMS_{psf_quartile}'
            tbl = hdul[extname].data
            (c0_rad, c1_rad, beta) = tbl['PSFSCALE'][0]
        c0_deg = (c0_rad * u_1.rad).to(u_1.deg)
        c1_deg = (c1_rad * u_1.rad).to(u_1.deg)
        return (c0_deg, c1_deg, beta)
    if __name__ == '__main__':
        psf_file = '/Users/vdk/miniforge3/envs/fermipy/share/fermitools/data/caldb/data/glast/lat/bcf/psf/psf_P8R3_SOURCE_V3_PSF.fits'
        for q in ['PSF0', 'PSF1', 'PSF2', 'PSF3']:
            (c0, c1, beta) = read_psf_scale_coeffs(psf_file, q)
            print(f'{q}: c0 = {c0:.3f}, c1 = {c1:.3f}, beta = {beta:.3f}')
    return


@app.cell
def _(compute_r68, psf_params_4, u_1):
    compute_r68(10000 * u_1.MeV, 2.848, 0.035, psf_params_4[2])
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()

