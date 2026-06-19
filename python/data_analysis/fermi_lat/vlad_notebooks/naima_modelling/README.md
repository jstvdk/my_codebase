# Naima Modelling for Gamma-Ray Source Analysis

## Table of Contents
1. [Scientific Background](#1-scientific-background)
2. [The Two Competing Scenarios](#2-the-two-competing-scenarios)
3. [Reference Paper: Hnatyk et al. 2022](#3-reference-paper-hnatyk-et-al-2022)
4. [Project Structure](#4-project-structure)
5. [The Spectrum Data](#5-the-spectrum-data)
6. [Physical Models and Parameters](#6-physical-models-and-parameters)
7. [Notebook Cell-by-Cell Guide](#7-notebook-cell-by-cell-guide)
8. [How to Interpret Results](#8-how-to-interpret-results)
9. [Running Your Own Analysis](#9-running-your-own-analysis)
10. [References](#10-references)

---

## 1. Scientific Background

### 1.1 The Problem: Unidentified Gamma-Ray Sources

Modern gamma-ray telescopes (Fermi-LAT, H.E.S.S., HAWC) have detected hundreds of sources emitting photons at energies from ~100 MeV to ~100 TeV. Many of these sources remain **unidentified** - we detect gamma-rays but don't know what astrophysical object produces them.

**The key question**: What physical process generates the gamma-rays?

### 1.2 Why This Matters

Identifying the emission mechanism tells us:
- What type of object we're observing (supernova remnant, pulsar wind nebula, etc.)
- Whether the source accelerates **protons** (hadronic) or **electrons** (leptonic)
- The total energy budget required - constraining the source's power
- Whether the source could be a "PeVatron" - accelerating particles to 10¹⁵ eV

### 1.3 The Naima Approach

[Naima](https://naima.readthedocs.io/) is a Python package that:
1. Takes an observed gamma-ray spectrum as input
2. Assumes a parent particle population (protons or electrons) with a parameterized energy distribution
3. Calculates the expected gamma-ray emission using known physics
4. Uses MCMC (Markov Chain Monte Carlo) to find the best-fit parameters and uncertainties

---

## 2. The Two Competing Scenarios

### 2.1 Hadronic Scenario (SNR Model)

**Physical picture**: Supernova remnant (SNR) shock accelerates cosmic ray **protons**

```
Supernova explosion
        ↓
   Expanding shock wave (v ~ 1000-10000 km/s)
        ↓
   Diffusive Shock Acceleration (DSA)
        ↓
   Relativistic protons (E up to ~PeV)
        ↓
   Protons collide with ambient gas (p + p → π⁰ + π± + ...)
        ↓
   Neutral pion decay: π⁰ → γ + γ
        ↓
   GAMMA-RAY EMISSION (E_γ ≈ 0.1 × E_proton)
```

**Key requirement**: Dense target material (gas) with number density n_H ~ 1-100 cm⁻³

**Characteristic signature**:
- "Pion bump" feature near 70 MeV (π⁰ rest mass / 2)
- Spectrum follows parent proton spectrum: Γ_γ ≈ Γ_proton

### 2.2 Leptonic Scenario (PWN Model)

**Physical picture**: Pulsar wind nebula (PWN) accelerates relativistic **electrons/positrons**

```
Spinning neutron star (pulsar)
        ↓
   Relativistic magnetized wind
        ↓
   Termination shock where wind meets SNR
        ↓
   Electron/positron acceleration (E up to ~PeV)
        ↓
   Electrons scatter background photons (Inverse Compton)
        ↓
   Low-energy photon (IR, CMB) → High-energy gamma-ray
        ↓
   GAMMA-RAY EMISSION (E_γ ≈ γ² × E_photon, where γ = E_e/m_e c²)
```

**Background photon fields**:
| Field | Origin | Temperature | Peak wavelength |
|-------|--------|-------------|-----------------|
| CMB | Big Bang relic radiation | 2.7 K | ~1 mm (microwave) |
| FIR | Dust emission | ~30-100 K | ~30-100 μm (far-infrared) |
| NIR | Starlight | ~3000-10000 K | ~1 μm (near-infrared/optical) |

**Key requirement**: High-energy electron population (no dense gas needed)

**Characteristic signature**:
- Softer spectrum at highest energies (Klein-Nishina suppression)
- Often associated with X-ray synchrotron nebula

---

## 3. Reference Paper: Hnatyk et al. 2022

### 3.1 Why We Use This Paper

Hnatyk et al. 2022 (MNRAS) analyzed the unidentified gamma-ray sources near magnetar SGR 1900+14:
- **4FGL J1908.6+0915e** (Fermi-LAT, extended)
- **HESS J1907+089 / HOTS J1907+091** (H.E.S.S.)
- **3HWC J1907+085** (HAWC)

They performed **exactly the type of analysis we want to replicate**:
- Combined multi-instrument spectra
- Fitted both hadronic and leptonic models
- Used naima for MCMC fitting
- Derived energy budgets and physical parameters

### 3.2 Key Information Extracted from the Paper

#### Spectral Data (Section 2.1 of paper)

**Fermi-LAT 4FGL J1908.6+0915e**:
- Energy range: 50 MeV - 1 TeV
- Spectrum: Power-law with Γ = 2.23 ± 0.098
- Pivot energy: 4.52 GeV
- Normalization: (1.01 ± 0.19) × 10⁻¹³ ph cm⁻² s⁻¹ MeV⁻¹

**H.E.S.S. HOTS J1907+091**:
- Energy range: 1 - 10 TeV
- Integral flux F(>1 TeV) = 4.3 × 10⁻¹³ cm⁻² s⁻¹
- Assumed index: Γ = 2.3 ± 0.2 (typical for Galactic VHE sources)
- Uncertainty: δF = 0.2F (20% systematic)

**HAWC 3HWC J1907+085**:
- Pivot energy: 7 TeV
- Normalization: 8.4 × 10⁻¹⁵ TeV⁻¹ cm⁻² s⁻¹
- Index: Γ = 2.95 ± 0.09

#### Physical Parameters (Section 3 and Table 1)

**Distance**: d = 12.5 kpc (from Davies et al. 2009, based on stellar cluster association)

**Target density for hadronic model**: n_H = 10 cm⁻³ (shell/halo density)

**Seed photon fields for leptonic model** (representative for TeV PWNe in HGPS):
| Field | Temperature | Energy Density | Why these values? |
|-------|-------------|----------------|-------------------|
| CMB | 2.7 K | 0.26 eV/cm³ | Universal, well-measured |
| FIR | 107 K | 1.19 eV/cm³ | Galactic dust emission model |
| NIR | 7906 K | 1.92 eV/cm³ | Galactic starlight model |

#### Best-Fit Results (Table 1)

**SNR Model (ECPL proton spectrum)**:
| Parameter | Value | Physical meaning |
|-----------|-------|------------------|
| Γ_p | 2.41 ± 0.03 | Proton spectral index (theory predicts ~2.0-2.4 for DSA) |
| E_cut | 185.2 ± 9.5 TeV | Maximum proton energy (related to acceleration limit) |
| W_p | 5.12 × 10⁵⁰ erg | Total energy in protons - **this is huge!** |
| χ²/ndf | 30.74/34 | Good fit (χ²/ndf ≈ 1 means model describes data well) |

**PWN Model (ECPL electron spectrum, 1 population)**:
| Parameter | Value | Physical meaning |
|-----------|-------|------------------|
| Γ_e | 3.08 ± 0.03 | Electron spectral index (steeper than protons due to cooling) |
| E_cut | 424.3 ± 21.1 TeV | Maximum electron energy |
| W_e | 8.80 × 10⁴⁹ erg | Total energy in electrons |
| χ²/ndf | 40.24/36 | Good fit |

### 3.3 Physical Interpretation from the Paper

**The energy budget problem**:
- Both models require W ~ 10⁵⁰ erg at d = 12.5 kpc
- A typical supernova releases ~10⁵¹ erg total
- This means ~10-50% of SN energy must go into accelerated particles
- This is only feasible for a **Hypernova** (E ~ 10⁵² erg) or millisecond magnetar scenario

**Why both models "work"**:
- The gamma-ray spectrum alone cannot distinguish hadronic vs leptonic
- Both can fit the data with reasonable χ²
- Additional information needed: molecular gas maps, X-ray observations, source morphology

---

## 4. Project Structure

```
naima_modelling/
├── README.md                         # This file
└── sgr1900+14/                       # Analysis directory
    │
    ├── spectrum_builder.py           # Builds combined Fermi+HESS+HAWC spectrum
    │
    ├── naima_models/                 # Physical model implementations
    │   ├── __init__.py               # Module exports
    │   ├── snr_pion_decay.py         # Hadronic: pp → π⁰ → γγ
    │   └── pwn_inverse_compton.py    # Leptonic: e + γ_bg → e + γ_HE
    │
    ├── naima/                        # Fitting notebooks
    │   ├── fit_snr_pion_decay.ipynb      # SNR (hadronic) fitting
    │   └── fit_pwn_inverse_compton.ipynb # PWN (leptonic) fitting
    │
    └── spectra/                      # Output directory for spectrum files
```

---

## 5. The Spectrum Data

### 5.1 What is a Gamma-Ray Spectrum?

A spectrum shows the **differential photon flux** as a function of energy:

```
dN/dE [photons / (cm² s GeV)]
```

This tells us: "How many photons per unit area, per unit time, per unit energy interval are arriving from the source?"

### 5.2 Why Combine Multiple Instruments?

| Instrument | Energy Range | Technique |
|------------|--------------|-----------|
| Fermi-LAT | 100 MeV - 1 TeV | Space-based pair conversion |
| H.E.S.S. | 100 GeV - 100 TeV | Ground-based Cherenkov |
| HAWC | 1 TeV - 100+ TeV | Ground-based water Cherenkov |

**The combination gives us 4+ decades in energy** (0.1 GeV to 100 TeV), which is essential for:
- Seeing spectral curvature (cutoffs)
- Breaking degeneracies between models
- Constraining both low-E and high-E behavior

### 5.3 The spectrum_builder.py Script

**What it does**:
1. Generates spectrum points from published analytical forms (or loads your Fermi data)
2. Combines Fermi + H.E.S.S. + (optionally) HAWC
3. Applies energy cuts (we use E > 200 MeV)
4. Formats data for naima fitting

**Key function**:
```python
spectrum = build_spectrum_for_naima(
    fermi_file=None,        # Path to your Fermi data, or None for synthetic
    energy_min=0.2*u.GeV,   # Lower energy cut
    n_fermi_bins=10,        # Number of Fermi energy bins
    n_hess_bins=10,         # Number of H.E.S.S. energy bins
    use_hawc=False          # Include HAWC data?
)
```

**Output format** (astropy QTable):
| Column | Unit | Description |
|--------|------|-------------|
| energy | GeV | Bin center energy |
| energy_edge_lo | GeV | Lower bin edge |
| energy_edge_hi | GeV | Upper bin edge |
| flux | 1/(cm² s GeV) | Differential flux |
| flux_error | 1/(cm² s GeV) | 1σ uncertainty |

---

## 6. Physical Models and Parameters

### 6.1 Particle Energy Distributions

Both models assume a parameterized energy distribution for the parent particles.

**Exponential Cutoff Power Law (ECPL)**:
```
N(E) = N₀ × (E/E₀)^(-Γ) × exp(-E/E_cut)
```

| Parameter | Symbol | Meaning |
|-----------|--------|---------|
| Amplitude | N₀ | Normalization (particles per unit energy at E₀) |
| Reference energy | E₀ | Energy where N₀ is defined (we use 1 TeV) |
| Spectral index | Γ | Power-law slope (larger = steeper = fewer high-E particles) |
| Cutoff energy | E_cut | Energy where spectrum steepens exponentially |

**Why ECPL?**
- Power-law is natural outcome of diffusive shock acceleration (Fermi mechanism)
- Cutoff represents maximum energy achievable (limited by age, size, losses)
- This is the standard assumption in the field

### 6.2 SNR Model: Pion Decay

**The physics** (naima.models.PionDecay):

1. Protons with spectrum N_p(E_p) hit target protons at rest
2. Inelastic collision produces pions: p + p → p + p + π⁰ + π± + ...
3. Neutral pions decay: π⁰ → γ + γ (mean lifetime 8.4 × 10⁻¹⁷ s)
4. Each gamma-ray carries ~E_p/10 on average

**Parameters we fit**:
| Parameter | Prior range | Physical constraint |
|-----------|-------------|---------------------|
| log₁₀(N₀) | [30, 42] | Must produce observed flux |
| Γ_p | [1.5, 3.5] | DSA theory: 2.0-2.4 typical |
| log₁₀(E_cut/TeV) | [0, 3] | 1 TeV to 1 PeV |

**Fixed parameters**:
| Parameter | Value | Justification |
|-----------|-------|---------------|
| n_H | 10 cm⁻³ | Shell density from paper |
| d | 12.5 kpc | Stellar cluster distance |
| E_min | 1 GeV | Below this, no significant γ-ray production |
| E_max | 1 PeV | Assumed maximum |

### 6.3 PWN Model: Inverse Compton

**The physics** (naima.models.InverseCompton):

1. Electrons with spectrum N_e(E_e) scatter background photons
2. In Thomson regime (low E_e): E_γ ≈ (4/3) γ² ε, where γ = E_e/(m_e c²), ε = photon energy
3. In Klein-Nishina regime (high E_e): scattering suppressed, E_γ ≈ E_e

**Seed photon fields** (defined in code):
```python
SEED_PHOTON_FIELDS = [
    ['CMB', 2.7 * u.K, 0.26 * u.eV / u.cm**3],
    ['FIR', 107 * u.K, 1.19 * u.eV / u.cm**3],
    ['NIR', 7906 * u.K, 1.92 * u.eV / u.cm**3],
]
```

**Why these specific values?**
- CMB is universal and precisely known
- FIR and NIR are from Galactic interstellar radiation field models
- These are "representative values for TeV PWNe in the HGPS" (H.E.S.S. Galactic Plane Survey)

**Parameters we fit**:
| Parameter | Prior range | Physical constraint |
|-----------|-------------|---------------------|
| log₁₀(N₀) | [30, 45] | Must produce observed flux |
| Γ_e | [2.0, 4.5] | Steeper than protons due to synchrotron cooling |
| log₁₀(E_cut/TeV) | [-1, 4] | 0.1 TeV to 10 PeV |

---

## 7. Notebook Cell-by-Cell Guide

### 7.1 SNR Notebook: `fit_snr_pion_decay.ipynb`

#### Cell 1: Imports
```python
import naima
from naima.models import ExponentialCutoffPowerLaw, PionDecay
```
**Why**: Load the fitting framework and physical models we need.

#### Cell 2: Load spectrum data
```python
data = build_spectrum_for_naima(fermi_file=None, energy_min=0.2*u.GeV, ...)
```
**Why**: Create the observed spectrum that we'll fit. Set `fermi_file` to your data path when you have real Fermi results.

#### Cell 3: Plot input data
**Why**: Always visualize your data before fitting! Check for:
- Energy coverage
- Error bar sizes
- Any obvious features (bumps, breaks, cutoffs)

#### Cell 4: Set up MCMC
```python
p0 = [35.0, 2.5, 2.3]  # Initial guess: [log10(N0), Γ, log10(Ecut/TeV)]
NWALKERS = 32   # Number of parallel "walkers" exploring parameter space
NBURN = 100     # Steps to discard (burn-in) while walkers find good region
NRUN = 500      # Steps to keep for final posterior distribution
```
**Why**:
- `p0`: Starting point for MCMC - should be roughly in the right ballpark
- More walkers = better exploration but slower
- Burn-in removes initial wandering before convergence

#### Cell 5: Run the sampler
```python
sampler, pos = naima.run_sampler(
    data_table=data,
    model=snr_pion_decay_ecpl,  # Our model function
    prior=snr_lnprior_ecpl,     # Prior probability function
    ...
)
```
**Why**: This is the core fitting step. MCMC explores parameter space, computing likelihood at each point. Takes several minutes.

#### Cell 6: Save diagnostics
```python
naima.save_diagnostic_plots(output_prefix, sampler, sed=True)
```
**Why**: Creates standard plots:
- `*_chain.png`: Parameter evolution (check for convergence)
- `*_corner.png`: Parameter correlations and marginalized distributions
- `*_sed.png`: Best-fit SED with data

#### Cell 7: Extract parameters
```python
q16, q50, q84 = np.percentile(chain, [16, 50, 84], axis=0)
```
**Why**:
- q50 = median = best estimate
- q84 - q50 = upper 1σ error
- q50 - q16 = lower 1σ error

#### Cell 8: Compute total energy
```python
Wp = compute_proton_energy(pars, model='ecpl')
```
**Why**: The **total energy in protons** is the key physical result. It tells us how much energy the source needs to power the emission.

#### Cell 9: Compute χ²
```python
chi2 = np.sum(((model - data) / error)**2)
```
**Why**: Goodness-of-fit metric. χ²/ndf ≈ 1 means good fit; >>1 means model doesn't describe data; <<1 means errors overestimated.

#### Cell 10: Plot SED
**Why**: Visual comparison of model vs data is essential. This is the figure you'll put in your paper/thesis.

#### Cell 11: Summary table
**Why**: Collect all results in one place for easy comparison with published values.

### 7.2 PWN Notebook: `fit_pwn_inverse_compton.ipynb`

The structure is identical to the SNR notebook, with these key differences:

#### Different model function
```python
model=pwn_ic_ecpl  # Instead of snr_pion_decay_ecpl
```

#### Additional plot: IC components
```python
# Plot contribution from each seed photon field separately
ax.plot(E, sed_cmb, '--', label='IC (CMB)')
ax.plot(E, sed_fir, '--', label='IC (FIR)')
ax.plot(E, sed_nir, '--', label='IC (NIR)')
```
**Why**: Shows which photon field dominates at which energy. Typically:
- NIR dominates at GeV energies
- CMB dominates at TeV energies (but with Klein-Nishina suppression at highest E)

---

## 8. How to Interpret Results

### 8.1 Comparing Hadronic vs Leptonic

After running both notebooks, compare:

| Metric | Hadronic (SNR) | Leptonic (PWN) | Which is better? |
|--------|----------------|----------------|------------------|
| χ²/ndf | Should be ~1 | Should be ~1 | Lower is better fit |
| W_p or W_e | ~10⁵⁰ erg | ~10⁴⁹-10⁵⁰ erg | Must be physically achievable |
| Γ | ~2.0-2.5 | ~2.5-3.5 | Must be consistent with theory |
| E_cut | ~100-1000 TeV | ~100-1000 TeV | Related to acceleration physics |

### 8.2 Physical Plausibility Checks

**For hadronic model**:
- Is there evidence of dense gas (molecular cloud) at the source location?
- Is W_p < 10⁵¹ erg (total SN energy)?
- Is W_p < 0.1 × E_SN reasonable for CR acceleration efficiency?

**For leptonic model**:
- Is there a known pulsar or PWN?
- Is W_e < spin-down energy of pulsar?
- Is there X-ray synchrotron emission (would confirm electron population)?

### 8.3 The Degeneracy Problem

**Important**: A good χ² for both models does NOT mean both are correct!

The gamma-ray spectrum alone often cannot distinguish the two scenarios. You need **multi-wavelength** and **multi-messenger** information:

| Observable | Favors hadronic | Favors leptonic |
|------------|-----------------|-----------------|
| Molecular gas at source | ✓ | |
| X-ray synchrotron nebula | | ✓ |
| Neutrino detection | ✓ (from π± decay) | |
| Radio synchrotron | | ✓ |
| Morphology matches gas | ✓ | |
| Morphology matches PWN | | ✓ |

---

## 9. Running Your Own Analysis

### 9.1 Quick Test (No Data Needed)

```bash
cd sgr1900+14/naima
jupyter notebook fit_snr_pion_decay.ipynb
# Run all cells - uses synthetic spectrum from published parameters
```

### 9.2 With Your Fermi-LAT Data

1. **Prepare your spectrum file** (from Fermi likelihood analysis):
```
# energy[GeV]  flux[1/(cm2 s GeV)]  flux_error[1/(cm2 s GeV)]
0.316  1.2e-10  2.4e-11
1.0    3.5e-11  7.0e-12
3.16   8.1e-12  1.6e-12
...
```

2. **Place file in spectra directory**:
```bash
cp your_fermi_spectrum.txt sgr1900+14/spectra/
```

3. **Edit notebook**:
```python
FERMI_DATA_FILE = "../spectra/your_fermi_spectrum.txt"
```

4. **Adjust parameters if needed**:
   - Change distance if your source is at different d
   - Modify n_H if you have density constraints
   - Adjust seed photon fields for different Galactic location

5. **Run both notebooks** and compare results

### 9.3 Production Run Settings

For publication-quality results, increase MCMC statistics:
```python
NWALKERS = 64    # More walkers
NBURN = 500      # Longer burn-in
NRUN = 2000      # More samples
```

Check convergence:
- Chain plot should be "fuzzy caterpillar" (well-mixed)
- Corner plot should show smooth distributions
- Run multiple times - results should be consistent

---

## 10. References

### Key Papers

1. **Hnatyk et al. 2022**, MNRAS, "Unveiling the nature of the unidentified gamma-ray sources 4FGL J1908.6+0915e, HESS J1907+089/HOTS J1907+091, and 3HWC J1907+085 in the sky region of the magnetar SGR 1900+14"
   - The reference paper we follow for methodology and parameters

2. **Zabalza 2015**, Proc. 34th ICRC, "naima: a Python package for inference of relativistic particle energy distributions from observed nonthermal spectra"
   - The naima package paper

3. **Aharonian 2004**, "Very High Energy Cosmic Gamma Radiation"
   - Textbook covering the physics of gamma-ray emission

### Useful Links

- **naima documentation**: https://naima.readthedocs.io/
- **Fermi-LAT 4FGL catalog**: https://fermi.gsfc.nasa.gov/ssc/data/access/lat/10yr_catalog/
- **H.E.S.S. HGPS**: https://www.mpi-hd.mpg.de/hfm/HESS/hgps/

### Software Dependencies

```bash
pip install naima matplotlib corner astropy numpy
```

---

## Questions?

If something is unclear:
1. Check the naima documentation
2. Look at the Hnatyk et al. 2022 paper (especially Section 3 and Table 1)
3. Ask your supervisor

Good luck with your analysis!
