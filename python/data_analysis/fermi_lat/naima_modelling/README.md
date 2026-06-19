# Naima Modelling for Gamma-Ray Source Analysis

This directory contains the framework for fitting gamma-ray spectral energy distributions (SEDs) using the [naima](https://naima.readthedocs.io/) Python package. The methodology follows **Hnatyk et al. 2022 (MNRAS)** for modeling unidentified gamma-ray sources.

## Overview

The analysis fits observed gamma-ray spectra (Fermi-LAT, H.E.S.S., HAWC) with physical models to determine:
- **Hadronic scenario (SNR)**: Cosmic ray protons interacting with ambient gas → pion decay → gamma-rays
- **Leptonic scenario (PWN)**: Relativistic electrons scattering background photons → Inverse Compton → gamma-rays

---

## Directory Structure

```
naima_modelling/
├── README.md                    # This file
└── sgr1900+14/                  # Analysis for SGR 1900+14 region
    ├── spectrum_builder.py      # Build combined multi-instrument spectra
    ├── spectra/                  # Output directory for spectrum files
    ├── naima_models/             # Physical model implementations
    │   ├── __init__.py
    │   ├── snr_pion_decay.py    # Hadronic (pion decay) models
    │   └── pwn_inverse_compton.py # Leptonic (IC) models
    └── naima/                    # Fitting notebooks
        ├── fit_snr_pion_decay.ipynb      # SNR hadronic fitting
        └── fit_pwn_inverse_compton.ipynb # PWN leptonic fitting
```

---

## Scripts and Modules

### 1. `spectrum_builder.py` - Spectrum Data Preparation

**Purpose**: Build combined gamma-ray spectra from multiple instruments for naima fitting.

**When to use**:
- Before running any fitting notebook
- When you have new Fermi-LAT spectral points to include
- To generate synthetic spectra from published parameters for testing

**Key functions**:

| Function | Description |
|----------|-------------|
| `build_spectrum_for_naima()` | Main function - builds combined Fermi+H.E.S.S.+HAWC spectrum |
| `load_fermi_from_file()` | Load actual Fermi-LAT data from your analysis |
| `generate_fermi_spectrum()` | Generate synthetic Fermi spectrum from published PL parameters |
| `generate_hess_spectrum()` | Generate H.E.S.S. spectrum from published parameters |
| `generate_hawc_spectrum()` | Generate HAWC spectrum from published parameters |

**Example usage**:
```python
from spectrum_builder import build_spectrum_for_naima
import astropy.units as u

# With your own Fermi data:
spectrum = build_spectrum_for_naima(
    fermi_file="path/to/your/fermi_spectrum.txt",
    energy_min=0.2 * u.GeV,
    use_hawc=False
)

# Or with synthetic data for testing:
spectrum = build_spectrum_for_naima(fermi_file=None)
```

**Input file format** (for Fermi data):
```
# energy[GeV]  flux[1/(cm2 s GeV)]  flux_error[1/(cm2 s GeV)]
0.316  1.2e-10  2.4e-11
1.0    3.5e-11  7.0e-12
...
```

---

### 2. `naima_models/snr_pion_decay.py` - Hadronic Models

**Purpose**: Implement gamma-ray emission from cosmic ray proton interactions (pp → π⁰ → γγ).

**When to use**:
- When testing the SNR (supernova remnant) hypothesis
- For sources associated with dense molecular clouds or shells
- When hadronic origin is suspected (hard spectrum, dense target material)

**Physical scenario**:
- CR protons accelerated at SNR shock
- Interact with ambient gas (density n_H ~ 10 cm⁻³)
- Produce neutral pions that decay to gamma-rays

**Available models**:

| Model | Function | Parameters |
|-------|----------|------------|
| Power-Law (PL) | `snr_pion_decay_pl()` | log₁₀(N₀), Γ |
| Exp. Cutoff PL (ECPL) | `snr_pion_decay_ecpl()` | log₁₀(N₀), Γ, log₁₀(E_cut) |

**Default parameters** (from Hnatyk et al. 2022):
- Distance: 12.5 kpc
- Target density: n_H = 10 cm⁻³
- E_min = 1 GeV, E_max = 1 PeV

---

### 3. `naima_models/pwn_inverse_compton.py` - Leptonic Models

**Purpose**: Implement gamma-ray emission from relativistic electrons via Inverse Compton scattering.

**When to use**:
- When testing the PWN (pulsar wind nebula) hypothesis
- For sources without dense target material
- When leptonic origin is suspected (associated pulsar, X-ray PWN)

**Physical scenario**:
- Electrons accelerated at PWN termination shock
- Scatter background photon fields (CMB, IR, starlight)
- Produce gamma-rays via Inverse Compton

**Seed photon fields** (representative for Galactic TeV PWNe):
| Field | Temperature | Energy Density |
|-------|-------------|----------------|
| CMB | 2.7 K | 0.26 eV/cm³ |
| FIR | 107 K | 1.19 eV/cm³ |
| NIR/Starlight | 7906 K | 1.92 eV/cm³ |

**Available models**:

| Model | Function | Parameters |
|-------|----------|------------|
| ECPL (1 population) | `pwn_ic_ecpl()` | log₁₀(N₀), Γ, log₁₀(E_cut) |
| ECBPL (broken PL) | `pwn_ic_ecbpl()` | log₁₀(N₀), Γ₁, Γ₂, log₁₀(E_br), log₁₀(E_cut) |

---

## Fitting Notebooks

### 4. `naima/fit_snr_pion_decay.ipynb` - SNR Hadronic Fitting

**Purpose**: Fit the pion decay model to observed gamma-ray spectrum.

**When to use**:
- To test if hadronic emission can explain the observed SED
- To derive CR proton energy budget (W_p)
- To constrain proton spectral index and cutoff energy

**Workflow**:
1. Load/build spectrum data
2. Set up MCMC parameters
3. Run naima sampler
4. Extract best-fit parameters and uncertainties
5. Compute total proton energy W_p
6. Generate diagnostic plots and SED

**Expected results** (Hnatyk et al. 2022, ECPL):
- Γ_p = 2.41 ± 0.03
- E_cut = 185.2 ± 9.5 TeV
- W_p = 5.12 × 10⁵⁰ erg

---

### 5. `naima/fit_pwn_inverse_compton.ipynb` - PWN Leptonic Fitting

**Purpose**: Fit the Inverse Compton model to observed gamma-ray spectrum.

**When to use**:
- To test if leptonic emission can explain the observed SED
- To derive electron energy budget (W_e)
- To constrain electron spectral index and cutoff energy
- To see contributions from different seed photon fields

**Workflow**:
1. Load/build spectrum data
2. Set up MCMC parameters
3. Run naima sampler
4. Extract best-fit parameters and uncertainties
5. Compute total electron energy W_e
6. Plot SED with individual IC components (CMB, FIR, NIR)

**Expected results** (Hnatyk et al. 2022, alternative ECPL):
- Γ_e = 3.08 ± 0.03
- E_cut = 424.3 ± 21.1 TeV
- W_e = 8.80 × 10⁴⁹ erg

---

## Typical Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  1. PREPARE FERMI DATA                                       │
│     - Run Fermi-LAT likelihood analysis                      │
│     - Extract spectral points to text file                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  2. BUILD COMBINED SPECTRUM                                  │
│     spectrum_builder.py                                      │
│     - Load Fermi data                                        │
│     - Add H.E.S.S./HAWC points                              │
│     - Apply energy cuts (E > 200 MeV)                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  3. FIT MODELS                                               │
│     Run fitting notebooks                                    │
│     ├── fit_snr_pion_decay.ipynb (hadronic)                 │
│     └── fit_pwn_inverse_compton.ipynb (leptonic)            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  4. COMPARE MODELS                                           │
│     - Compare χ²/ndf                                         │
│     - Compare energy budgets (W_p vs W_e)                   │
│     - Check physical plausibility                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start

1. **Test with synthetic data** (no Fermi data needed):
   ```bash
   cd sgr1900+14/naima
   jupyter notebook fit_snr_pion_decay.ipynb
   ```
   Run all cells - it will use published spectral parameters.

2. **With your own Fermi data**:
   - Place your spectrum file in `sgr1900+14/spectra/`
   - Edit the notebook: `FERMI_DATA_FILE = "../spectra/my_fermi_spectrum.txt"`
   - Run the notebook

---

## References

- **Hnatyk et al. 2022**, MNRAS, "Unveiling the nature of the unidentified gamma-ray sources 4FGL J1908.6+0915e, HESS J1907+089/HOTS J1907+091, and 3HWC J1907+085 in the sky region of the magnetar SGR 1900+14"
- **naima documentation**: https://naima.readthedocs.io/
- **Fermi-LAT 4FGL catalog**: Abdollahi et al. 2020, ApJS, 247, 33

---

## Dependencies

```
numpy
astropy
naima
matplotlib
emcee (installed with naima)
corner (for diagnostic plots)
```

Install with:
```bash
pip install naima matplotlib corner
```
