# Gamma-ray modelling of the SGR 1900+14 region with naima

A self-contained **tutorial project**: fit hadronic and leptonic cosmic-ray
emission models to the gamma-ray spectrum of the sources around the magnetar
SGR 1900+14, reproducing and extending

> Hnatyk R., Hnatyk B., Zhdanov V., Voitsekhovskyi V., 2022, *MNRAS* **516**, 4196.

This one file explains **what each notebook does, what spectra we use and why, and
— most importantly — how to plug in your own spectra** (you will have others).

## Contents
- [Installation (fresh machine)](#installation-fresh-machine)
- [Quick start](#quick-start)
- [The scientific question](#the-scientific-question)
- [What each notebook / file does](#what-each-notebook--file-does)
- [The spectrum data: what we use and why](#the-spectrum-data-what-we-use-and-why)
- [How we connect Fermi with H.E.S.S. / HAWC](#how-we-connect-fermi-with-hess--hawc)
- [▶ Adding your own spectrum (step by step)](#-adding-your-own-spectrum-step-by-step)
- [The two physical models](#the-two-physical-models)
- [▶ Reusing the models for another source or dataset](#-reusing-the-models-for-another-source-or-dataset)
- [Interpreting the results](#interpreting-the-results)
- [Reference values & further reading](#reference-values--further-reading)

---

## Installation (fresh machine)

You need Python with [naima](https://naima.readthedocs.io). The easiest
reproducible route is **conda** (via Miniforge). Do this once on a new machine.
Open the notebooks in whatever you prefer afterwards (your IDE, classic Jupyter, …).

**1. Install Miniforge** (a minimal conda; skip if you already have conda/mamba).

```bash
# macOS (Apple Silicon or Intel) and Linux — downloads & runs the installer:
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh        # accept defaults, then restart the terminal
```
On Windows, download and run the Miniforge3 installer from
<https://github.com/conda-forge/miniforge>, then use the "Miniforge Prompt".

**2. Get the project files** onto the machine (clone the repo, or copy the
`sgr1900+14/` folder), and `cd` into `sgr1900+14/`.

**3. Create the environment** — one command, from the provided spec:

```bash
conda env create -f environment.yml      # creates an env called "naima"
conda activate naima
```

<details><summary>Prefer to do it by hand (or use pure pip)?</summary>

```bash
# conda, manual:
conda create -n naima -c conda-forge python=3.12 naima=0.10.2 matplotlib ipykernel
conda activate naima

# OR pure pip (inside a fresh virtual environment):
python -m venv venv && source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
</details>

**4. Check it works:**

```bash
python -c "import naima; print('naima', naima.__version__)"   # -> naima 0.10.2
```

That's it. The same `environment.yml` / `requirements.txt` reproduce the exact
toolchain this project was built with (Python 3.12, naima 0.10.2, astropy 7,
numpy 2, emcee 3, corner 2).

---

## Quick start

```bash
conda activate naima                 # the env you created above
python spectrum_tools.py             # (re)generate every spectrum in spectra/
```

**Read in this order:** `BAYESIAN_PRIMER.md` → `naima_tutorial.ipynb` → a fitting
notebook → `plot_results.ipynb`.

```
sgr1900+14/
├── README.md                          # << this guide
├── environment.yml / requirements.txt # the software environment (see Installation)
├── BAYESIAN_PRIMER.md                 # Bayesian stats in a nutshell (1 page)
├── spectrum_tools.py                  # build standardised spectra (real + butterfly)
├── plotting.py                        # reusable paper-style SED plot functions (take fit params)
├── FERMI_CATALOG.txt                  # OPTIONAL: real Fermi-LAT SED points (fermipy output);
│                                      #   only needed to (re)build the real-Fermi baseline
├── spectra/                           # generated ECSV spectra (+ spectra/README.md)
├── naima_models/
│   ├── hadronic.py                    # PionDecay + co-accelerated e- (IC + Synchrotron)
│   └── leptonic.py                    # Inverse Compton (+ Synchrotron)
└── notebooks/
    ├── naima_tutorial.ipynb
    ├── fit_hadronic_pion_decay.ipynb
    ├── fit_leptonic_inverse_compton.ipynb
    └── plot_results.ipynb
```


---

## The scientific question

Three spatially-coincident unidentified gamma-ray sources sit near the magnetar
SGR 1900+14 (distance d ≈ 12.5 kpc):

| Source | Instrument | Band |
|--------|-----------|------|
| 4FGL J1908.6+0915e | Fermi-LAT | 50 MeV – 1 TeV |
| HESS J1907+089 / HOTS J1907+091 | H.E.S.S. | 1 – 10 TeV |
| 3HWC J1907+085 | HAWC | ~1 – 100 TeV |

**Are the gamma rays made by protons (hadronic) or electrons (leptonic)?** We fit
both models to the same spectrum and compare goodness of fit, spectral shape, and
the *required particle energy* to judge which is more plausible. naima does the
fitting the Bayesian/MCMC way — if that's unfamiliar, read
[`BAYESIAN_PRIMER.md`](BAYESIAN_PRIMER.md) first.

---

## What each notebook / file does

| File | What it does | Spectra it uses |
|------|--------------|-----------------|
| [`BAYESIAN_PRIMER.md`](BAYESIAN_PRIMER.md) | One-page intro to Bayesian fitting: prior · likelihood · posterior · MCMC, with a coin-flip example you can run in 10 lines. | – |
| [`notebooks/naima_tutorial.ipynb`](notebooks/naima_tutorial.ipynb) | **Foundations.** What naima is; the chain *particle spectrum → radiative process → flux at Earth*; the three particle distributions and four radiative processes (Synchrotron, Inverse Compton, Bremsstrahlung, PionDecay) with runnable example plots; what a fit needs as input (data table, model function, prior) and produces as output; a tiny live MCMC. | `combined_real_baseline.ecsv` (for the demo) |
| [`notebooks/fit_hadronic_pion_decay.ipynb`](notebooks/fit_hadronic_pion_decay.ipynb) | **Full hadronic fit, step by step:** load data → inspect SED → build the PionDecay (+ co-accelerated e⁻) model → priors → MCMC → convergence diagnostics (chains, corner) → best-fit parameters → total proton energy **W_p** → goodness of fit → component SED → cross-check on the equal-weight dataset → conclusion. | baseline `combined_real_baseline.ecsv`; cross-check `combined_fermi_hess.ecsv`; HAWC overlay |
| [`notebooks/fit_leptonic_inverse_compton.ipynb`](notebooks/fit_leptonic_inverse_compton.ipynb) | Same structure for the **leptonic (Inverse Compton)** model; headline output is the electron energy **W_e**. | same as above |
| [`notebooks/plot_results.ipynb`](notebooks/plot_results.ipynb) | **Publication-style figures** in the paper's Fig. 4/5 style: data + total + every component (PionDecay/IC split by seed field) + Synchrotron at B = 1 & 5 µG, plus a side-by-side hadronic-vs-leptonic panel. Plots best-fit parameters — no MCMC re-run. | `combined_real_baseline.ecsv` + `hawc_3hwc_propagated.ecsv` |
| [`spectrum_tools.py`](spectrum_tools.py) | Builds every standardised spectrum from published parameters / real catalogs. Run it to regenerate `spectra/`. **This is the file you edit to add a telescope.** | writes `spectra/*.ecsv` |
| [`naima_models/hadronic.py`](naima_models/hadronic.py), [`leptonic.py`](naima_models/leptonic.py) | The physics: build the particle distribution + radiative model from a parameter vector; provide the `*_model(pars, data)`, `lnprior`, `compute_Wp/We`, `INITIAL`, `LABELS`. | – |
| [`plotting.py`](plotting.py) | **Reusable paper-style SED plot functions** — `plot_hadronic_sed(pars, data, hawc)`, `plot_leptonic_sed(...)`, `plot_comparison(...)`. Pass a fit's parameter vector (e.g. the posterior medians) and get the Fig. 4/5 figure. Used by `plot_results.ipynb` and callable from any fit notebook. | – |

---

## The spectrum data: what we use and why

A spectrum here is the **differential photon flux** dN/dE [1/(cm² s GeV)] vs energy.

The source is faint and the instruments give us different things:

- **Fermi-LAT** — a **real binned SED** ([`FERMI_CATALOG.txt`](FERMI_CATALOG.txt),
  a fermipy output): 6 detected points + 2 upper limits, 50 MeV–1 TeV.
- **H.E.S.S. / HAWC** — only a published **power-law fit + uncertainty band**
  (a "butterfly"), *no per-bin points*. To fit a point-based model we must
  **sample** the power law into points and assign each an error.

Because *how* you build and weight those points is a real choice,
[`spectrum_tools.py`](spectrum_tools.py) produces **two parallel datasets** (all as
naima-native ECSV files in [`spectra/`](spectra/), see
[`spectra/README.md`](spectra/README.md)):

**A. Baseline — real Fermi + propagated TeV (the scientific default).**
Real Fermi points (real errors + upper limits); H.E.S.S./HAWC sampled *sparsely*
with **bow-tie errors** propagated from the power-law fit covariance,
δF/F = √[(σ_N0/N0)² + (ln(E/E_piv)·σ_Γ)²]; fit with **inverse-variance weighting**.
→ `combined_real_baseline.ecsv`.

**B. Cross-check — flat 0.2·F equal weighting (paper reproduction).**
20 + 20 log-spaced points with a constant δF = 0.2·F, so every point weighs equally.
→ `combined_fermi_hess.ecsv`. The fit notebooks refit on this and show the
parameters barely move → the conclusions are **robust to the data construction**.

### Standardised column format (every spectrum file)

| Column | Unit | Meaning |
|--------|------|---------|
| `energy` | GeV | bin centre (geometric mean of edges) |
| `energy_lo`, `energy_hi` | GeV | bin edges |
| `flux` | 1/(cm² s GeV) | differential flux dN/dE (the limit value for UL rows) |
| `flux_error_lo`, `flux_error_hi` | 1/(cm² s GeV) | 1σ errors (asymmetric allowed) |
| `ul` | bool | upper-limit flag |
| `instrument`, `group` | – | bookkeeping |

These are exactly the columns `naima.run_sampler` expects, so the files load with
no conversion. `table.meta["keywords"]["cl"]["value"]` holds the upper-limit
confidence level.

---

## How we connect Fermi with H.E.S.S. / HAWC

**Why combine:** each instrument covers a different band; together they span
~0.05 GeV – 100 TeV (≈ 6 decades). That lever arm is what lets us see spectral
curvature/cutoffs, break model degeneracies, and constrain the parent particle
spectrum end to end.

**Common footing:** all instruments are expressed as the *same* quantity (dN/dE in
the same units) in the *same* standardised table; the combined table is just the
per-instrument tables **stacked and sorted in energy**. naima fits one model across
the whole table at once.

**Weighting** (this is the subtle part): a fit weights each point by 1/σ². If one
band had many tightly-binned points it could dominate and ignore the others. Two
ways out, both provided:
- *Inverse-variance with realistic errors* (baseline): with a handful of real
  Fermi points and propagated TeV errors of comparable size, the bands balance
  **naturally**. This is the statistically standard choice.
- *Equal weighting* (cross-check): same relative error (0.2·F) and same point count
  per band → each point/band contributes equally by construction. Simple, ad hoc.

**Caveat:** sampling a butterfly into N points is never perfectly rigorous — the
points aren't independent (they come from one 2-parameter fit), so results depend
slightly on how many you draw. Keep TeV sampling **sparse**; treat the TeV band as
the weak power-law *prior* it really is.

**HAWC is comparison-only** (as in the paper): the fit uses Fermi + H.E.S.S.; the
steeper HAWC spectrum is over-plotted, not fitted. **Upper limits** are passed to
naima as upper limits, not detections.

### What you actually need (inputs vs outputs)

There are two layers — don't confuse them:

- **`spectrum_tools.py`** = the tool that *builds* the spectra. It holds the
  published power-law parameters (`PUBLISHED`) and the functions
  (`butterfly_spectrum`, `standardise_points`, `load_fermi_catalog`,
  `combine_spectra`). *(An older `spectrum_builder.py` from a previous version has
  been removed — `spectrum_tools.py` fully replaces it.)*
- **`spectra/*.ecsv`** = the *outputs* it writes — the standardised tables the
  notebooks actually load.

Run `python spectrum_tools.py` to regenerate `spectra/`. **Only one input file is
ever needed: `FERMI_CATALOG.txt`** (the real Fermi SED), and *only* for the
real-Fermi baseline. Everything else (the H.E.S.S./HAWC butterflies and the flat
cross-check Fermi) is computed from the `PUBLISHED` power-law parameters and needs
**no input file at all**. If `FERMI_CATALOG.txt` is absent, `spectrum_tools.py`
prints a note, skips `combined_real_baseline*.ecsv`, and still builds everything
else — point the notebooks at `combined_fermi_hess.ecsv` in that case (or supply
your own Fermi spectrum, next section).

The real Fermi points also live, already converted, inside
`spectra/fermi_real_4fgl.ecsv`, so deleting `FERMI_CATALOG.txt` does not lose them
— it only removes the ability to rebuild that file from the raw catalog.

---

## ▶ Adding your own spectrum (step by step)

You will have other spectra. There are two cases depending on what you have. Run
these snippets from the project root (`sgr1900+14/`) with `conda activate naima`.

### Case 1 — you have real flux points (energies, fluxes, errors)

Use `standardise_points`. It accepts astropy `Quantity` arrays in *any* units
(they're converted internally), asymmetric errors, and upper limits.

```python
import numpy as np, astropy.units as u
from spectrum_tools import standardise_points, save_spectrum

# your measured SED (example numbers; units can be anything compatible)
E      = np.array([0.3, 1.0, 3.0, 10.0]) * u.TeV
E_lo   = np.array([0.2, 0.6, 2.0,  6.0]) * u.TeV
E_hi   = np.array([0.6, 2.0, 6.0, 20.0]) * u.TeV
flux   = np.array([1.2e-12, 2.0e-13, 3.0e-14, 4.0e-15]) * u.Unit('1/(cm2 s TeV)')
err    = 0.15 * flux                       # symmetric 15% here; pass lo/hi separately if asymmetric
is_ul  = np.array([False, False, False, True])   # last bin is an upper limit

t = standardise_points(
    energy=E, flux=flux,
    flux_error_lo=err, flux_error_hi=err,
    energy_lo=E_lo, energy_hi=E_hi,
    instrument='MAGIC', source='My Source',
    ul=is_ul, cl=0.95,
)
save_spectrum(t, 'spectra/magic_mysource.ecsv')
```

Reading from a plain text file first? Load it however you like (`np.loadtxt`,
`astropy.table.Table.read`, `pandas`) into arrays, attach units, then call
`standardise_points`. For a fermipy SED table specifically, there's a ready-made
loader: `load_fermi_catalog('path/to/catalog.txt')`.

### Case 2 — you only have a published power law (a butterfly)

Add an entry to the `PUBLISHED` dictionary in
[`spectrum_tools.py`](spectrum_tools.py) and call `butterfly_spectrum`. Give the
normalisation either directly (`norm` at `pivot_energy`) **or** as an integral flux
(`integral_flux` above `integral_emin`).

```python
import numpy as np, astropy.units as u
from spectrum_tools import butterfly_spectrum, save_spectrum

params = {
    'instrument': 'MAGIC', 'source': 'My Source',
    'pivot_energy': 1.0 * u.TeV,
    'norm': 1.0e-12 * u.Unit('1/(cm2 s TeV)'),   # OR: 'integral_flux'+'integral_emin'
    'index': 2.4, 'index_err': 0.15,
    'energy_min': 0.1 * u.TeV, 'energy_max': 10.0 * u.TeV,
    'n_bins': 20,                # points for the flat (equal-weight) model
    # for the propagated (bow-tie) model:
    'rel_norm_err': 0.15,        # fractional normalisation error at the pivot
    'prop_pivot': 1.0 * u.TeV,   # decorrelation/pivot energy
    'n_bins_baseline': 5,        # sparse points (a few per decade)
}

# sparse + realistic errors (recommended), or error_model='flat' for equal weight
t = butterfly_spectrum(params, error_model='propagated')
save_spectrum(t, 'spectra/magic_mysource.ecsv')
```

### Combine your spectrum with the others and fit it

```python
from spectrum_tools import load_spectrum, combine_spectra, save_spectrum

fermi = load_spectrum('spectra/fermi_real_4fgl.ecsv')
mine  = load_spectrum('spectra/magic_mysource.ecsv')
combined = combine_spectra(fermi, mine)          # stacks + sorts in energy
save_spectrum(combined, 'spectra/my_combined.ecsv')
```

Then point a fitting notebook at it — change **one line** in the "load data" cell:

```python
data = load_spectrum('../spectra/my_combined.ecsv')
```

…and run the rest unchanged. The model functions, priors, MCMC, W_p/W_e and plots
all work on any standardised table.

### Sanity checks (worth doing once)
```python
import naima
naima.utils.validate_data_table(load_spectrum('spectra/my_combined.ecsv'))  # no error = good
naima.plot_data(load_spectrum('spectra/my_combined.ecsv'), sed=True)        # eyeball it
```

**Tips & gotchas**
- The only *required* columns are `energy`, `flux`, and either `flux_error` or
  `flux_error_lo`+`flux_error_hi`. `standardise_points`/`butterfly_spectrum` fill
  the rest.
- Units are checked by astropy — a unit mismatch raises rather than silently
  corrupting the fit.
- A brand-new `instrument` name gets `group = 0` (fine for fitting); add it to
  `GROUP_ID` in `spectrum_tools.py` if you want a distinct group id.
- Keep sampled (butterfly) points **sparse**; don't fake precision by drawing many
  points from one power-law fit.
- To regenerate the whole `spectra/` folder from the published parameters, just run
  `python spectrum_tools.py`.

---

## The two physical models

Both use an **Exponential-Cutoff Power-Law** parent spectrum
N(E) = N₀ (E/E₀)^(−Γ) exp(−E/E_cut), normalised at **E₀ = 1 TeV**. Fixed for both:
d = 12.5 kpc, B = 3 µG (synchrotron), seed photon fields CMB (2.7 K, 0.26 eV/cm³),
FIR (107 K, 1.19 eV/cm³), NIR (7906 K, 1.92 eV/cm³).

**Hadronic** ([`hadronic.py`](naima_models/hadronic.py)) — PionDecay(protons) +
co-accelerated e⁻ (N₀,e = K_ep·N₀,p) giving IC + Synchrotron.

| Free parameter | prior | note |
|---|---|---|
| log₁₀(N₀,p / eV⁻¹) | [30, 42] | proton normalisation at 1 TeV |
| Γ_p | [1.5, 3.5] | shock acceleration predicts ~2.0–2.4 |
| log₁₀(E_cut/TeV) | [0, 3.5] | 1 TeV – ~3 PeV |
| K_ep | [0, 0.1] | electron-to-proton energy fraction |
| n_H [cm⁻³] | [1, 50] | ambient gas density |

> **Degeneracy:** pion-decay flux ∝ N₀,p·n_H, so the data constrain only the
> *product* (N₀ and n_H anti-correlate; W_p ∝ 1/n_H). Kept free on purpose so it's
> visible in the corner plot.

**Leptonic** ([`leptonic.py`](naima_models/leptonic.py)) — InverseCompton(e⁻) +
Synchrotron; electron integration from E_e,min = 10 GeV.

| Free parameter | prior | note |
|---|---|---|
| log₁₀(N₀,e / eV⁻¹) | [30, 45] | electron normalisation at 1 TeV |
| Γ_e | [2.0, 4.5] | usually steeper than protons (cooling) |
| log₁₀(E_cut/TeV) | [−1, 4] | 0.1 TeV – 10 PeV |

---

## ▶ Reusing the models for another source or dataset

You can run the **same hadronic / leptonic analysis on a different source** (or new
spectrum points) without rewriting the physics. The full recipe:

1. **Build your spectrum file** from your points — see
   [Adding your own spectrum](#-adding-your-own-spectrum-step-by-step)
   (`standardise_points` → `combine_spectra` → `save_spectrum`).
2. **Point a fit notebook at it** — copy `fit_hadronic_pion_decay.ipynb` (or the
   leptonic one) as a template and change the *one* "load data" line to your file.
3. **Set the source-specific physics in `CONFIG`** (see below).
4. **Update the starting guess** `INITIAL` (and `LABELS` if you change the
   parameters) so the MCMC starts in a sensible place for the new source.
5. Run → fit → `plot_hadronic_sed(pars, …)` / `plot_leptonic_sed(...)`.

### Where the source-specific knobs live: `CONFIG`

Each model module begins with a `CONFIG` dict and a `SEED_PHOTON_FIELDS` list —
these are the **fixed inputs that depend on the source, not on the data**. For a
new source you edit *these*, not the fitting code.

**`naima_models/hadronic.py`:**
```python
CONFIG = {
    "distance": 12.5 * u.kpc,   # <-- change for your source
    "E0":       1.0  * u.TeV,   # reference energy for N0 (usually leave as is)
    "Ep_min":   1.0  * u.GeV,   # proton integration / Wp bounds
    "Ep_max":   1e6  * u.GeV,
    "Ee_min":   1.0  * u.GeV,   # co-accelerated-electron integration bounds
    "Ee_max":   1e6  * u.GeV,
    "B":        3.0  * u.uG,    # <-- ambient magnetic field (synchrotron)
}
SEED_PHOTON_FIELDS = [          # <-- IC target photons at the source's location
    ["CMB", 2.7  * u.K, 0.26 * u.eV / u.cm**3],
    ["FIR", 107  * u.K, 1.19 * u.eV / u.cm**3],
    ["NIR", 7906 * u.K, 1.92 * u.eV / u.cm**3],
]
```

**`naima_models/leptonic.py`** has the same idea (note `Ee_min = 10 GeV` there).

| Knob | When to change it |
|------|-------------------|
| `distance` | **Always** for a new source — it sets the flux↔luminosity conversion and therefore W_p / W_e. |
| `SEED_PHOTON_FIELDS` | **Leptonic / IC**: the interstellar radiation field differs by Galactic location. Update temperatures & energy densities (e.g. from a GALPROP/popescu ISRF model) for your source. |
| `B` | If you have a magnetic-field estimate (affects synchrotron, and the implied W_e for a fixed synchrotron flux). |
| `Ee_min` / `Ep_min` / `Ee_max` / `Ep_max` | The energy range the particle energy `W` is integrated over. W is sensitive to the lower bound — keep it consistent with what you want to quote. |
| `E0` | Leave at 1 TeV unless you have a reason; it's just the reference energy for `N0`. |

### Reuse the model, or write a new one?

- **Same physics, different source/data → reuse.** Just edit `CONFIG` /
  `SEED_PHOTON_FIELDS` and `INITIAL`. Nothing else changes.
- **Different physics → new module.** If you need another particle shape (e.g. a
  broken power law) or a process not yet wired in (e.g. Bremsstrahlung, SSC, a
  second population), copy `hadronic.py`/`leptonic.py` and keep the **same public
  interface** so the notebooks and `plotting.py` keep working:

  | name | role |
  |------|------|
  | `<name>_model(pars, data)` | returns the total flux Quantity at the data energies (for `naima.run_sampler`) |
  | `lnprior(pars)` | flat log-prior (`naima.uniform_prior` bounds) |
  | `build_models(pars)` | dict of radiative components (for plotting) |
  | `electron_distribution(pars)` | the electron spectrum (used by `plotting.py` for synchrotron) |
  | `compute_Wp` / `compute_We` | total particle energy in erg |
  | `INITIAL`, `LABELS`, `CONFIG`, `SEED_PHOTON_FIELDS` | starting guess, plot labels, fixed inputs |

  As long as those exist, `plot_hadronic_sed` / `plot_leptonic_sed` / `run_sampler`
  work on your new model unchanged.

---

## Interpreting the results

Compare the two fits **on the same data**:

| Metric | Hadronic | Leptonic | Reading |
|--------|----------|----------|---------|
| χ²/ndf | ~1 | ~1 | both acceptable; lower = better spectral match |
| index Γ | ~2.4 (natural) | ~3.1 (steep) | hadronic is closer to acceleration theory |
| energy | W_p ~ 5×10⁵⁰ erg | W_e ~ 10⁵⁰ erg | must be physically suppliable |

**Honest takeaway:** an SED fit constrains *parameters and energetics*; it does not
by itself decide the mechanism — both fit. Both also need ~10⁵⁰ erg in particles at
12.5 kpc (demanding for an ordinary ~10⁵¹ erg supernova → the paper invokes a
magnetar-related hypernova). The verdict needs independent clues (molecular gas →
hadronic; X-ray/radio synchrotron nebula → leptonic; neutrinos → hadronic;
morphology). Also note **E_cut is poorly constrained** (data stop at ~10 TeV).

---

## Reference values & further reading

**Hnatyk et al. 2022, Table 1** (d = 12.5 kpc; our fits reproduce these to ~1%):
- Hadronic ECPL: Γ_p = 2.41, E_cut = 185 TeV, K_ep = 0.0041, n_sh ≈ 9.8 cm⁻³, **W_p = 5.12×10⁵⁰ erg**, χ²/ndf = 30.7/34.
- Leptonic ECPL: Γ_e = 3.08, E_cut = 424 TeV, **W_e = 8.80×10⁴⁹ erg**, χ²/ndf = 40.2/36.

**References**
1. Hnatyk et al. 2022, MNRAS 516, 4196 — the paper we reproduce.
2. Zabalza 2015, Proc. 34th ICRC, arXiv:1509.03319 — the naima package.
3. Hogg & Foreman-Mackey 2018, arXiv:1710.06068 — *Using MCMC* (friendly).
4. naima docs: <https://naima.readthedocs.io>

**Dependencies:** `naima` (which brings `astropy`, `numpy`, `scipy`, `emcee`,
`corner`, `h5py`), plus `matplotlib` and `ipykernel`. See `environment.yml`.
