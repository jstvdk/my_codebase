# Fermi-LAT Analysis Project

This project contains two complementary Fermi-LAT analysis setups optimized for different scientific goals:

1. **[Fermi_0.2-500GeV/](Fermi_0.2-500GeV/)** - Spectral/SED studies with maximum statistics
2. **[Fermi_1-500GeV/](Fermi_1-500GeV/)** - Morphology studies with best angular resolution

Each analysis is self-contained with its own configuration files, scripts, and notebooks.

---

## Table of Contents

1. [Analysis Types Overview](#analysis-types-overview)
2. [Quick Start](#quick-start)
3. [Model Comparison Workflow](#model-comparison-workflow)
4. [Configuration Parameters Explained](#configuration-parameters-explained)
5. [Analysis Comparison](#analysis-comparison)
6. [Directory Structure](#directory-structure)
7. [Tips and Troubleshooting](#tips-and-troubleshooting)

---

## Analysis Types Overview

### 1. Morphology Analysis (1-500 GeV)

**Location:** [Fermi_1-500GeV/](Fermi_1-500GeV/)

**Purpose:** Study spatial structure, source extension, localization, and morphology. Compare different source models.

**Key Characteristics:**
- **Energy Range:** 1-500 GeV (higher threshold for better PSF)
- **Event Class:** CLEAN (256) - lowest background, best PSF
- **PSF Configuration:** Split by quality (PSF1/PSF2/PSF3 separate)
- **Energy Dispersion:** Disabled (not needed for spatial studies)

**Best For:**
- Source extension measurements
- TS (Test Statistic) maps
- Source localization
- Model comparison (point vs extended, single vs multiple sources)
- Multi-source deblending
### 2. Spectral/SED Analysis (0.2-500 GeV)

**Location:** [Fermi_0.2-500GeV/](Fermi_0.2-500GeV/)

**Purpose:** Measure spectral energy distributions (SEDs), spectral indices, flux in energy bins, and spectral curvature.

**Key Characteristics:**
- **Energy Range:** 0.2-500 GeV (lower threshold for more statistics)
- **Event Class:** SOURCE (128) - maximum photon statistics
- **PSF Configuration:** All PSF types combined (evtype 3 = FRONT+BACK)
- **Energy Dispersion:** Enabled (critical for accurate spectral reconstruction)

**Best For:**
- Spectral energy distributions (SEDs)
- Flux measurements in energy bins
- Spectral index determination
- Detecting spectral cutoffs or features


---

## Quick Start

### Prerequisites

```bash
conda activate fermipy
```

### For Spectral/SED Studies

```bash
cd Fermi_0.2-500GeV
python run_baseline_analysis.py config_0.2-500.yaml
```

### For Morphology Studies

```bash
cd Fermi_1-500GeV
python run_baseline_analysis.py config_1-500_CLEAN.yaml
```

---

## Model Comparison Workflow

The morphology analysis (1-500 GeV) includes a systematic workflow to test different source models:

### Models to Compare

| Model | Description | Notebook |
|-------|-------------|----------|
| A | 1 extended catalog source (4FGL) | Baseline |
| B | 2 point sources | `two_point_source_analysis.ipynb` |
| C | 2 extended sources | `extension_test_analysis.ipynb` |
| D | 1 point + 1 extended | `extension_test_analysis.ipynb` |
| E | Physics-constrained (fixed SNR + residual) | `constrained_source_analysis.ipynb` |

### Recommended Workflow

```
Step 1: Create baseline
        python run_baseline_analysis.py config_1-500_CLEAN.yaml

Step 2: Compare 2 point sources vs catalog
        jupyter notebook two_point_source_analysis.ipynb
        -> Outputs: AIC comparison, localized positions

Step 3a: If Model B preferred -> Test if sources are extended
         jupyter notebook extension_test_analysis.ipynb
         -> Uses gta.extension() to test TS_ext
         -> Determines if point or extended spatial model

Step 3b: If Model A preferred -> Try physics-constrained model
         jupyter notebook constrained_source_analysis.ipynb
         -> Fix one source at known SNR/Magnetar position
         -> Let other source find residual emission
```

### Statistical Comparison

**For non-nested models:** Use AIC (Akaike Information Criterion)
```
AIC = 2k - 2*logL    (lower is better)

Interpretation of Delta(AIC) = AIC_new - AIC_baseline:
  < -10: Strong preference for new model
  < -2:  Moderate preference for new model
  > 2:   Moderate preference for baseline
  > 10:  Strong preference for baseline
```

**For extension testing:** Use TS_ext
```
TS_ext = 2*(logL_extended - logL_point)

Interpretation:
  < 4:   No evidence for extension (point source)
  4-16:  Marginal evidence
  > 16:  Significant extension (~4 sigma)
  > 25:  Strong extension (~5 sigma)
```

---

## Configuration Parameters Explained

### Data Section

```yaml
data:
  evfile: '/path/to/PH.txt'     # Photon event file
  scfile: '/path/to/SC.fits'    # Spacecraft file
```

- **evfile:** Contains all detected gamma-ray events (energy, position, time)
- **scfile:** Spacecraft pointing and livetime data for exposure calculation

### Selection Section

```yaml
selection:
  emin: 200 or 1000    # MeV - energy threshold
  emax: 500000         # MeV - upper limit
  evclass: 128 or 256  # SOURCE or CLEAN
  evtype: 3 or 8/16/32 # All PSF or PSF split
  glon: 43.1249        # ROI center
  glat: 0.4301
  zmax: 90
  filter: "(DATA_QUAL>0)&&(LAT_CONFIG==1)"
```

#### Event Class (`evclass`)

| Class | Code | Statistics | Background | Best For |
|-------|------|------------|------------|----------|
| SOURCE | 128 | High | Higher | Spectral studies |
| CLEAN | 256 | Lower | Lowest | Morphology studies |

#### Event Type (`evtype`)

| Value | Meaning | Use Case |
|-------|---------|----------|
| 3 | FRONT+BACK (all) | Spectral analysis |
| 8 | PSF1 (best quality) | Morphology (component) |
| 16 | PSF2 (medium) | Morphology (component) |
| 32 | PSF3 (standard) | Morphology (component) |

### GTlike Section

```yaml
gtlike:
  irfs: 'P8R3_SOURCE_V3' or 'P8R3_CLEAN_V3'
  edisp: True or False
  edisp_disable: ['isodiff', 'galdiff']
```

**Critical:** IRFs must match event class!
- SOURCE (128) -> `P8R3_SOURCE_V3`
- CLEAN (256) -> `P8R3_CLEAN_V3`

**Energy Dispersion:**
- Enable (`True`) for spectral studies - affects SED accuracy
- Disable (`False`) for morphology - PSF dominates, speeds up analysis

### Components Section (PSF Split)

For morphology analysis with PSF-split data:

```yaml
components:
  - selection: {evtype: 8}
    model:
      isodiff: '/path/to/iso_P8R3_CLEAN_V3_PSF1_v1.txt'
  - selection: {evtype: 16}
    model:
      isodiff: '/path/to/iso_P8R3_CLEAN_V3_PSF2_v1.txt'
  - selection: {evtype: 32}
    model:
      isodiff: '/path/to/iso_P8R3_CLEAN_V3_PSF3_v1.txt'
```

Each PSF type requires its own isotropic template.

### Model Section

```yaml
model:
  src_roiwidth: 15
  galdiff: '/path/to/gll_iem_v07.fits'
  isodiff: '/path/to/iso_P8R3_SOURCE_V3_v1.txt'  # For non-PSF-split only
  catalogs: '/path/to/gll_psc_v35.fit'
```

- **galdiff:** Galactic diffuse emission model (required)
- **isodiff:** Isotropic background (use in `model:` for evtype 3, or in `components:` for PSF split)
- **catalogs:** 4FGL source catalog

---

## Analysis Comparison

| Parameter | Spectral (0.2-500 GeV) | Morphology (1-500 GeV) |
|-----------|----------------------|----------------------|
| **Energy Range** | 0.2-500 GeV | 1-500 GeV |
| **Event Class** | SOURCE (128) | CLEAN (256) |
| **PSF Config** | evtype: 3 (all) | evtype: 8/16/32 (split) |
| **Energy Dispersion** | True | False |
| **Isodiff** | Single template | Per-PSF (3 templates) |
| **IRFs** | P8R3_SOURCE_V3 | P8R3_CLEAN_V3 |
| **Primary Output** | SEDs, spectra | TS maps, extension |
| **Angular Resolution** | ~0.5-1 deg | ~0.1-0.5 deg |

---

## Directory Structure

```
vlad_notebooks/
├── README.md                              # This file
│
├── Fermi_0.2-500GeV/                      # Spectral/SED Analysis
│   ├── config_0.2-500.yaml               # Main config
│   ├── run_baseline_analysis.py          # Baseline script
│   ├── initial_0.2-500.ipynb             # Initial analysis
│   └── output_*/                         # Output products
│
└── Fermi_1-500GeV/                        # Morphology Analysis
    ├── config_1-500_CLEAN.yaml           # CLEAN config (recommended)
    ├── config_1-500.yaml                 # SOURCE config (alternative)
    ├── run_baseline_analysis.py          # Baseline script
    │
    │   ## Analysis Notebooks
    ├── two_point_source_analysis.ipynb   # Compare 2 point vs 1 extended
    │   - Load baseline (Model A with catalog source)
    │   - Generate TS/NPred maps
    │   - Delete catalog source, add 2 point sources
    │   - Localize both sources
    │   - Fit and compare AIC
    │
    ├── extension_test_analysis.ipynb     # Test source extension
    │   - Load two-point model from previous notebook
    │   - Run gta.extension() on Src1 (RadialDisk + RadialGaussian)
    │   - Run gta.extension() on Src2
    │   - Decision tree: point vs extended for each
    │   - Refit with optimal spatial models
    │
    ├── constrained_source_analysis.ipynb # Physics-constrained model
    │   - Fix one source at known SNR/Magnetar position
    │   - Extended disk spatial model for SNR
    │   - Free position for residual source
    │   - Compare with catalog model using AIC
    │
    └── output_*/                         # Output products
```

---

## Tips and Troubleshooting

### Configuration Tips

1. **Always use absolute paths** in config files
2. **Match event class and IRFs** - mixing causes systematic errors
3. **Use PSF split only for morphology** - spectral studies need statistics
4. **Enable edisp for spectral studies** - essential for accurate SEDs

### Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| CLEAN for spectral | Lose statistics | Use SOURCE (128) |
| SOURCE for morphology | High background | Use CLEAN (256) with PSF split |
| edisp off for SED | Wrong spectral shape | Enable edisp: True |
| Single isodiff with PSF split | Wrong background | Use per-PSF templates |
| Wrong IRFs | ~20% flux error | Match IRF to event class |

### Troubleshooting

**"Setup failed" or "File not found"**
- Check all paths exist and use absolute paths
- Verify fermitools environment is activated

**"Fit quality is not 3"**
- Run `gta.optimize()` before `gta.fit()`
- Free fewer sources initially

**Model comparison gives unexpected results**
- Check both models converged (fit_quality = 3)
- Verify source names match between add_source() and sed()
- Save intermediate ROI states with `gta.write_roi()`

**VSCode Jupyter "notebook controller is DISPOSED"**
- Close notebook, reload VSCode window (Cmd+Shift+P -> Reload)
- Or run from terminal: `jupyter notebook filename.ipynb`

---

## References

- **Fermipy:** https://fermipy.readthedocs.io/
- **Fermi Science Tools:** https://fermi.gsfc.nasa.gov/ssc/data/analysis/
- **4FGL Catalog:** https://fermi.gsfc.nasa.gov/ssc/data/access/lat/12yr_catalog/
