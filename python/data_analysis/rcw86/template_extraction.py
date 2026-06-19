import marimo

__generated_with = "0.13.6"
app = marimo.App()


@app.cell
def _():
    from astropy.io import fits
    import numpy as np
    import matplotlib.pyplot as plt

    for fname in [
        "/Volumes/Crucial/astrodata/data/rcw86/radio/G315.4-2.3_Irefit.fits",
        "/Volumes/Crucial/astrodata/data/rcw86/radio/G315.42.3_I_CropI.fits",
        "/Volumes/Crucial/astrodata/data/rcw86/radio/G315.4-2.3_DeepRM_Crop.fits",
        "/Volumes/Crucial/astrodata/data/rcw86/radio/G315.4-2.3_ShallowRM.fits",
    ]:
        with fits.open(fname) as hdul:
            hdr0 = hdul[0].header
            print(f"{fname}: NAXIS = {hdr0['NAXIS']}")
            if hdr0['NAXIS'] >= 3:
                print("  CTYPE3 =", hdr0.get('CTYPE3'))
                print("  CRVAL3 =", hdr0.get('CRVAL3'), hdr0.get('CDELT3'), hdr0.get('CRPIX3'))
            print()
    return fits, np, plt


@app.cell
def _(fits):
    ire_fits_file = "/Volumes/Crucial/astrodata/data/rcw86/radio/G315.4-2.3_Irefit.fits"
    with fits.open(ire_fits_file) as ffile:
        hdu = ffile[0]
        data4d = hdu.data
        header = hdu.header


    data4d.shape
    return data4d, header


@app.cell
def _(data4d, np):
    data3d = np.squeeze(data4d)
    data3d.shape
    return (data3d,)


@app.cell
def _(data3d):
    slice0 = data3d[0,:,:]
    slice1 = data3d[1,:,:]
    slice2 = data3d[2,:,:]
    slice3 = data3d[3,:,:]
    slice4 = data3d[4,:,:]

    return slice0, slice1, slice2, slice4


@app.cell
def _():
    return


@app.cell
def _():
    (-0.0008) > (-0.005)
    return


@app.cell
def _(data3d, np):
    np.nanmin(data3d[0][3])
    return


@app.cell
def _(data3d):
    data3d[0].shape
    return


@app.cell
def _(np, slice0):
    abs(np.nanmin(slice0))
    return


@app.cell
def _():
    return


@app.cell
def _(np, plt, slice0):
    plt.figure(figsize=(12,12))
    plt.imshow(
        slice0, 
        #vmin = np.nanmin(slice0), 
        vmin = 0,
        vmax = abs(np.nanmin(slice0))
    )
    plt.colorbar()
    plt.show()
    #plt.savefig("0channel2.png", dpi = 500)
    return


@app.cell
def _(np, plt, slice1):
    plt.figure(figsize=(12,12))
    plt.imshow(
        slice1, 
        vmin = 0, 
        vmax = abs(np.nanmin(slice1))
    )
    plt.colorbar()
    plt.show()
    #plt.savefig("1channel.png", dpi = 200)
    return


@app.cell
def _(np, plt, slice2):
    plt.figure(figsize=(12,12))
    plt.imshow(
        slice2, 
        vmin = 0, 
        vmax = abs(np.nanmin(slice2))
    )
    plt.colorbar()
    plt.show()
    #plt.savefig("0channel2.png", dpi = 200)
    return


@app.cell
def _(np, plt, slice2):
    plt.figure(figsize=(12,12))
    plt.imshow(
        slice2, 
        vmin = np.nanmin(slice2), 
        vmax = abs(np.nanmin(slice2))
    )
    plt.colorbar()
    plt.show()
    #plt.savefig("0channel2.png", dpi = 200)
    return


@app.cell
def _(np, plt, slice4):
    plt.figure(figsize=(12,12))
    plt.imshow(
        slice4, 
        vmin = 0, 
        vmax = abs(np.nanmin(slice4))
    )
    plt.colorbar()
    plt.show()
    #plt.savefig("0channel2.png", dpi = 200)
    return


@app.cell
def _(header):
    from astropy.wcs import WCS

    wcs = WCS(header)
    return (wcs,)


@app.cell
def _(header):
    header
    return


@app.cell
def _():
    from astropy.visualization import simple_norm
    return (simple_norm,)


@app.cell
def _(wcs):
    wcs
    return


@app.cell
def _(wcs):
    wcs2d = wcs.celestial
    wcs2d
    return (wcs2d,)


@app.cell
def _(np, plt, simple_norm, slice1, wcs2d):
    vmin, vmax = np.nanpercentile(slice1, [5,99])
    levels = [(vmin + (vmax - vmin)*f) for f in [0.8, 0.9]]
    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(projection=wcs2d)

    norm = simple_norm(slice1, 'sqrt', percent=99.5)
    ax.imshow(slice1, norm=norm)

    contours = ax.contour(slice1, levels = levels, colors = 'red')
    ax.set_label('RA')
    ax.set_label('dec')
    plt.grid(color='white', ls='dotted')
    plt.show()
    return


@app.cell
def _(slice0, wcs2d):
    def _():
        import numpy as np
        import matplotlib.pyplot as plt
        from astropy.visualization import simple_norm
    
        plot_slice = slice0

        # 1) compute min/max of the map (ignore NaNs)
        min_val = np.nanmin(plot_slice)
        max_val = np.nanmax(plot_slice)

        # 2) build contour levels at 50%, 70%, 90% through the range
        fractions = [0.001, 0.002, 0.003]
        levels = [min_val + f * (max_val - min_val) for f in fractions]

        # 3) plot image + contours
        fig = plt.figure(figsize=(8,8))
        ax  = fig.add_subplot(1,1,1, projection=wcs2d)

        # show the map with a sqrt stretch for visibility
        norm = simple_norm(plot_slice, 'sqrt', percent=99.5)
        ax.imshow(plot_slice, origin='lower', norm=norm)

        # draw the %-level contours
        cs = ax.contour(
            plot_slice,
            levels=levels,
            colors=['red','red','red'],  # one color per level
            linewidths=1.5,
            origin='lower'
        )

        # label each contour with its percentage
        fmt = {level: f"{int(f*100)} %" for level, f in zip(levels, fractions)}
        ax.clabel(cs, cs.levels, fmt=fmt, inline=True, fontsize=11, colors='white')

        # clean up axes
        ax.set_xlabel("Right Ascension")
        ax.set_ylabel("Declination")
        ax.grid(color='white', ls='dotted')

        plt.tight_layout()
        return plt.show()


    _()
    return


if __name__ == "__main__":
    app.run()
