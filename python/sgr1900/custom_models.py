import astropy.units as u
import numpy as np
import naima


def ElectronIC(pars, data):
    # Match parameters to ECPL properties, and give them the appropriate units
    amplitude = pars[0] / u.eV
    e_0 = (10 ** pars[1]) * u.TeV
    alpha = pars[2]
    e_cutoff = (10 ** pars[3]) * u.TeV

    ECPL = naima.models.ExponentialCutoffPowerLaw(amplitude, e_0, alpha, e_cutoff)
 
    IC = naima.models.InverseCompton(
        ECPL,
        seed_photon_fields=[
        ["CMB", 2.7 * u.K, 0.26 * u.eV / u.cm**3],
        ["FIR", 107 * u.K, 1.19 * u.eV / u.cm**3],
        ["NIR", 7906 * u.K, 1.92 * u.eV / u.cm**3]
        ],
        Eemin=10 * u.GeV,
    )

    model = IC.flux(data, distance=12.5 * u.kpc).to(data["flux"].unit)

    elec_energy = np.logspace(1, 15, 1000) * u.eV
    nelec = ECPL(elec_energy)

    We = IC.compute_We(Eemin=10 * u.GeV, Eemax = 1e6 * u.GeV)


    return model, (elec_energy, nelec), We

def lnprior_electrons(pars):
    logprob = (
        naima.uniform_prior(pars[0], 1e32, 1e43) + 
        naima.uniform_prior(pars[1], -5, 1) + 
        naima.uniform_prior(pars[2], 1.5, 4) + 
        naima.uniform_prior(pars[3], -5, 3)
    )
    return logprob

def PionDecay_PL(pars, proton_energy, data):
    amplitude_p =  pars[0] / u.eV  # Норма для протонів
    e_0 = 10 ** pars[1] * u.TeV
    alpha = pars[2]
    
    # PowerLaw для протонів (PionDecay)
    PL_p = naima.models.PowerLaw(amplitude_p, e_0, alpha)
    Pion = naima.models.PionDecay(PL_p, nh=10 / u.cm**3)
    
    # PowerLaw для електронів (InverseCompton) з K_ep=0.02
    K_ep = 0.02  # Фіксоване відношення
    amplitude_e = K_ep * amplitude_p
    PL_e = naima.models.PowerLaw(amplitude_e, e_0, alpha)
    IC = naima.models.InverseCompton(PL_e, seed_photon_fields=[
        ["CMB", 2.7 * u.K, 0.26 * u.eV / u.cm**3],
        ["FIR", 107 * u.K, 1.19 * u.eV / u.cm**3],
        ["NIR", 7906 * u.K, 1.92 * u.eV / u.cm**3]
    ])
    elec_energy = np.logspace(7, 15, 1000) * u.eV
    distance = 12.5 * u.kpc

    model = Pion.flux(data, distance=distance) + IC.flux(data, distance=distance)

    
    nelec = PL_e(elec_energy)

    # Save a realization of the particle distribution to the metadata blob
    proton_dist = Pion.particle_distribution(proton_energy)
    # Compute the total energy in protons above 1 TeV for this realization
    E_max = 1000 * u.TeV  
    Wp = Pion.compute_Wp(Epmin=1 * u.GeV, Epmax=E_max)
    We = IC.compute_We(Eemin=1 * u.GeV, Eemax=E_max)

    # Return the model, proton distribution and energy in protons to be stored
    # in metadata blobs
    return model, (proton_energy, proton_dist), Wp, (elec_energy, nelec), We


def lnprior_protons(pars):
        
    logprob = (naima.uniform_prior(pars[0], 1e32, 1e4) + 
               naima.uniform_prior(pars[1], -5, 1) + 
               naima.uniform_prior(pars[2], 1.5, 4)
    ) 
    return logprob