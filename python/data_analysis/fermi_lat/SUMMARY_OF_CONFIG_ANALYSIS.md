# Fermi-LAT Analysis Summary

## Inconsistencies Found and Fixed

### 1. ❌ Critical Bug: Source Name Mismatch (FIXED)

**File:** `point_extended_1-500.ipynb`

**Problem:**
```python
# Cell 12: Sources added with these names
gta.add_source("Src1_pointlike", {...})
gta.add_source("Src2_extended", {...})

# Cell 22: SED calculation uses WRONG names
sed1 = gta.sed('Src1_ext_and_point', ...)  # ❌ Doesn't exist!
sed2 = gta.sed('Src2_ext_and_point', ...)  # ❌ Doesn't exist!
```

**Solution:**
Use matching names:
```python
sed1 = gta.sed('Src1_pointlike', ...)
sed2 = gta.sed('Src2_extended', ...)
```

---

### 2. ❌ Isotropic Template Configuration (FIXED)

**Problem:** `config_1-500.yaml` used a single isotropic template for PSF1/2/3 split analysis.

**Before:**
```yaml
components:
  - selection: {evtype: 8}   # PSF1
  - selection: {evtype: 16}  # PSF2
  - selection: {evtype: 32}  # PSF3

model:
  isodiff: 'iso_P8R3_SOURCE_V3_v1.txt'  # ❌ Same for all!
```

**After:**
```yaml
components:
  - selection: {evtype: 8}
    model:
      isodiff: 'iso_P8R3_SOURCE_V3_PSF1_v1.txt'  # ✓ Specific
  - selection: {evtype: 16}
    model:
      isodiff: 'iso_P8R3_SOURCE_V3_PSF2_v1.txt'  # ✓ Specific
  - selection: {evtype: 32}
    model:
      isodiff: 'iso_P8R3_SOURCE_V3_PSF3_v1.txt'  # ✓ Specific
```

---

### 3. ℹ️ Path Inconsistencies (Expected)

**Observation:** Notebooks use different filesystem paths:
- `initial_1-500.ipynb`: macOS paths (`/Users/vdk/...`)
- Other notebooks: Linux paths (`/home/vlad/...`)

**Note:** This is expected when working across different systems. **Solution:** Update paths in config files for each system.

---

## Files Created

### 1. `run_baseline_analysis.py` ✨

**Purpose:** Simple, clean script to create baseline model from config.

**Usage:**
```bash
python run_baseline_analysis.py config_1-500.yaml
```

**What it does:**
1. Loads config file
2. Runs `gta.setup()`
3. Performs initial optimization
4. Frees sources within 3° of ROI center
5. Runs final optimization and fit
6. Saves baseline model as `baseline.npy`

**No command-line options** - everything comes from the config!

---

### 2. `README.md` 📖

Complete guide for:
- Quick start
- Configuration explanation
- Workflow examples
- Tips and troubleshooting

---

## Simplified Architecture

```
Config File (YAML)
      ↓
run_baseline_analysis.py
      ↓
GTAnalysis (fermipy)
      ↓
Output: baseline.npy
```

**Single source of truth:** The config file contains all paths and parameters.

---

## Configuration Templates

**Important:** This 1-500 GeV dataset is for **MORPHOLOGY** studies (spatial structure, source extension).
For **SED/spectral** studies, use your separate lower-energy dataset.

### CLEAN Analysis (Recommended) ⭐
**File:** `config_1-500_CLEAN.yaml`

```yaml
selection:
  evclass: 256  # CLEAN - lower background

gtlike:
  irfs: 'P8R3_CLEAN_V3'
  edisp: False  # Disabled for morphology at high energies

components:
  - selection: {evtype: 8}
    model:
      isodiff: 'iso_P8R3_CLEAN_V3_PSF1_v1.txt'
  # ... PSF2, PSF3
```

**Best for:** Morphology studies with cleanest backgrounds and best PSF

---

### SOURCE Analysis (Alternative)
**File:** `config_1-500.yaml`

```yaml
selection:
  evclass: 128  # SOURCE - more statistics

gtlike:
  irfs: 'P8R3_SOURCE_V3'
  edisp: False  # Disabled for morphology at high energies

components:
  - selection: {evtype: 8}
    model:
      isodiff: 'iso_P8R3_SOURCE_V3_PSF1_v1.txt'
  # ... PSF2, PSF3
```

**Use for:** When you need higher statistics, but accept higher background

---

### Energy Dispersion (edisp)

**What is it?** Accounts for difference between measured and true photon energy.

**For this 1-500 GeV analysis:**
- ✅ **Disabled (False)** - correct choice for morphology at high energies
- Effect of edisp is small at GeV energies
- Disabling speeds up analysis significantly
- Morphology studies don't require precise energy measurements

**When to enable edisp:**
- Spectral/SED studies (use your lower-energy dataset)
- Below ~1 GeV where energy resolution matters more
- When you need accurate energy measurements

---

## Workflow

### Step 1: Configure

Edit `config_1-500.yaml` with paths for your system:

```yaml
data:
  evfile: '/your/path/to/PH.txt'
  scfile: '/your/path/to/SC.fits'

model:
  galdiff: '/your/path/to/gll_iem_v07.fits'
  catalogs: '/your/path/to/gll_psc_v35.fit'

components:
  - selection: {evtype: 8}
    model:
      isodiff: '/your/path/to/iso_P8R3_SOURCE_V3_PSF1_v1.txt'
  # ... etc
```

### Step 2: Create Baseline

```bash
conda activate fermipy
python run_baseline_analysis.py config_1-500.yaml
```

### Step 3: Test Models

In notebook or script:

```python
from fermipy.gtanalysis import GTAnalysis

# Load baseline
gta = GTAnalysis('config_1-500.yaml', logging={'verbosity': 3})
gta.load_roi('baseline')

# Test your models
gta.delete_source('4FGL J1908.6+0915e')
gta.add_source('MySource', {...})
gta.optimize()
gta.fit()
```

---

## Key Differences: Before vs After

### Before (Notebooks)

❌ Hardcoded paths in notebook cells
❌ Manual steps scattered across cells
❌ Difficult to reproduce
❌ Wrong isotropic template setup
❌ Source naming bugs

### After (Script + Config)

✅ All paths in config file
✅ One command to create baseline
✅ Easy to reproduce
✅ Correct isotropic templates
✅ Clean, simple workflow

---

## Configuration Checklist

When setting up a new analysis:

- [ ] Copy config template
- [ ] Update data paths (`evfile`, `scfile`)
- [ ] Update catalog path
- [ ] Update galactic diffuse path (`galdiff`)
- [ ] Update isotropic template paths (one per PSF type)
- [ ] Set ROI center (`glon`, `glat`)
- [ ] Set energy range (`emin`, `emax`)
- [ ] Choose event class (`evclass`: 128=SOURCE, 256=CLEAN)
- [ ] Match IRFs to event class
- [ ] Set output directory (use format: `output_{emin/1000}-{emax/1000}GeV_{evclass}_{roiwidth}deg_PSF{types}_{coordsys}`)
- [ ] Verify all paths exist!

---

## Common Mistakes to Avoid

1. **Wrong isodiff for PSF split** ❌
   - Don't use single template for PSF1/2/3
   - Use separate template per PSF type

2. **Mismatched event class and IRFs** ❌
   - SOURCE (128) must use `P8R3_SOURCE_V3`
   - CLEAN (256) must use `P8R3_CLEAN_V3`

3. **Source name typos** ❌
   - Make sure names match in `add_source()` and `sed()`

4. **Relative paths** ⚠️
   - Use absolute paths in configs to avoid confusion

5. **Forgetting conda environment** ❌
   - Always activate: `conda activate fermipy`

---

## Troubleshooting

### "Config file not found"
- Check you're in the right directory
- Use absolute path: `python run_baseline_analysis.py /full/path/to/config.yaml`

### "Isotropic template not found"
- Check paths in config match your fermitools installation
- Usually in: `$CONDA_PREFIX/share/fermitools/refdata/fermi/galdiffuse/`

### "Setup failed"
- Check all data files exist
- Check you have write permissions for output directory

### SED calculation fails with "Source not found"
- Check source name spelling
- Use `gta.print_model()` to see exact source names

---

## Next Steps

1. ✅ Fix source names in `point_extended_1-500.ipynb`
2. ✅ Use `run_baseline_analysis.py` for baseline creation
3. ✅ Update config paths for your system
4. Test the workflow on your data

---

## Questions?

Refer to:
- `README.md` - Quick start and configuration guide
- Fermipy docs: https://fermipy.readthedocs.io/
- This file - Summary of changes and fixes

**Remember:** The config file is your single source of truth!
