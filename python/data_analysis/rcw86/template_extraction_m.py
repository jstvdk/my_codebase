import marimo

__generated_with = "0.13.6"
app = marimo.App()


@app.cell
def _():
    from astropy.io import fits
    import numpy as np


    for fname in [
        "/Users/vdk/data/rcw86/G315.4-2.3_Irefit.fits",
        "/Users/vdk/data/rcw86/G315.42.3_I_CropI.fits",
        "/Users/vdk/data/rcw86/G315.4-2.3_DeepRM_Crop.fits",
        "/Users/vdk/data/rcw86/G315.4-2.3_ShallowRM.fits",
    ]:
        with fits.open(fname) as hdul:
            hdr0 = hdul[0].header
            print(f"{fname}: NAXIS = {hdr0['NAXIS']}")
            if hdr0['NAXIS'] >= 3:
                print("  CTYPE3 =", hdr0.get('CTYPE3'))
                print("  CRVAL3 =", hdr0.get('CRVAL3'), hdr0.get('CDELT3'), hdr0.get('CRPIX3'))
            print()
    return


if __name__ == "__main__":
    app.run()
