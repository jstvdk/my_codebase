import astropy.units as u
import numpy as np
import naima


def IC_ECPL(pars, data):
    """
    Exponential-cutoff power-law electron spectrum + IC gamma rays.

    Parameters
    ----------
    pars : array-like
        [log10_norm, index, log10_Ecut_TeV]
        log10_norm      : log10 of electron PL amplitude at 1 TeV [1/eV]
        index           : electron spectral index
        log10_Ecut_TeV  : log10 of cutoff energy in TeV.
    data : astropy.table.Table
        Must contain column "energy" with photon energies.

    Returns
    -------
    model : astropy.units.Quantity
        Differential photon flux dN/dE at data["energy"] (sum of all IC
        components: CMB + IR + starlight).
    (electron_energy, electron_dist) : tuple
        Electron energies and corresponding dN/dE.
    We : astropy.units.Quantity
        Total energy in electrons above 1 GeV.
    """
    log10_norm, index, log10_Ecut_TeV = pars

    # Electron energy grid stored as a blob (100 MeV – 100 TeV, adjust if needed)
    electron_energy = np.logspace(8, 14, 100) * u.eV

    # ECPL electron spectrum
    e0 = 1 * u.TeV
    amplitude = 10**log10_norm / u.eV              # dN/dE amplitude
    e_cutoff = 10**log10_Ecut_TeV * u.TeV

    ECPL = naima.models.ExponentialCutoffPowerLaw(
        amplitude=amplitude,
        e_0=e0,
        alpha=index,
        e_cutoff=e_cutoff,
    )

    # Seed photon fields (as in your PWN paper figure)
    seed_photon_fields = [
        "CMB",  # T = 2.7 K, u = 0.26 eV/cm3 (built-in)
        ["IR", 107 * u.K, 1.19 * u.eV / u.cm**3],
        ["SL", 7906 * u.K, 1.92 * u.eV / u.cm**3],
    ]

    IC = naima.models.InverseCompton(
        ECPL,
        seed_photon_fields=seed_photon_fields,
        Eemin=100 * u.MeV,   # electron integration limits (for kernel)
        Eemax=1e5 * u.GeV,
    )

    distance = 12.5 * u.kpc          # PWN distance from the paper
    energy = data["energy"]          # photon energies
    model = IC.flux(energy, distance=distance)  # dN/dE

    # Electron distribution blob
    electron_dist = ECPL(electron_energy)

    # Total energy in electrons (you can change Emin to 1 TeV if that’s what you used)
    We = IC.compute_We(Eemin=1 * u.GeV)

    return model, (electron_energy, electron_dist), We


def IC_ECPL_lnprior(pars):
    """
    Log-prior for [log10_norm, index, log10_Ecut_TeV] for IC model.

    - index: uniform between 1.5 and 3.5
    - log10_norm: uniform between 35 and 55  (broad; tweak after first runs)
    - log10_Ecut_TeV: uniform between 0 and 3   (1–1000 TeV)
    """
    log10_norm, index, log10_Ecut_TeV = pars
    logprob = 0.0

    logprob += naima.uniform_prior(index, 1.5, 3.5)
    logprob += naima.uniform_prior(log10_norm, 35.0, 55.0)
    logprob += naima.uniform_prior(log10_Ecut_TeV, 0.0, 3.0)

    return logprob
