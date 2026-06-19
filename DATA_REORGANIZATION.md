# Data Reorganization

Large generated analysis artifacts were moved out of this Git working tree on
2026-06-19. The original folder layout inside the repository was preserved with
symbolic links, so existing notebooks and scripts can continue to use the same
relative paths.

External data root:

```text
/Users/vdk/software/my_codebase_data
```

External nested repository root:

```text
/Users/vdk/software/my_codebase_external_repos
```

Moved paths:

```text
python/data_analysis/fermi_lat/output_sgr_with_model
python/data_analysis/fermi_lat/rcw86_100MeV500GeV/output_rcw_100MeV500GeV_2008_2015
python/data_analysis/fermi_lat/rcw86/output_rcw
python/data_analysis/fermi_lat/rcw86/output_rcw_2008_2025_7.5deg_1GeV_PSF1-3
python/data_analysis/fermi_lat/rcw86/output_rcw_2016_2025
python/data_analysis/fermi_lat/rcw86/output_rcw_2016_2025 copy
python/data_analysis/fermi_lat/rcw86/output_rcw_celestial
python/data_analysis/fermi_lat/rcw86/output_rcw_celestial_3GeV_PSF1-3
python/data_analysis/fermi_lat/rcw86/output_rcw_celestial_6years
python/data_analysis/fermi_lat/sgr1900/output_sgr
python/data_analysis/fermi_lat/sgr1900/output_sgr_1GeV_15deg_PSF1-3_GAL
python/data_analysis/fermi_lat/sgr1900/output_sgr_1GeV_15deg_PSF1-3_GAL_datareload
python/data_analysis/fermi_lat/sgr1900/output_sgr_1GeV_15deg_PSF1-3_GAL_TEST_IRF
python/data_analysis/fermi_lat/sgr1900/output_sgr_1GeV_15deg_region
python/data_analysis/fermi_lat/sgr1900/output_sgr_1GeV_15deg_two_sources
python/data_analysis/fermi_lat/sgr1900/output_sgr_1GeV_15deg_two_sources_GAL
python/data_analysis/fermi_lat/sgr1900/output_sgr_5GeV_FRONTBACK
python/data_analysis/fermi_lat/sgr1900/output_sgr_5GeV_PSF2PSF3
python/data_analysis/fermi_lat/sgr1900/output_sgr_with_model
python/data_analysis/fermi_lat/updated_pipeline/Fermi_0.2-500GeV
python/data_analysis/fermi_lat/updated_pipeline/Fermi_1-500GeV
python/data_analysis/fermi_lat/updated_pipeline.tar.gz
python/data_analysis/fermi_lat/vlad_notebooks/data
python/data_analysis/fermi_lat/vlad_notebooks/Fermi_0.2-500GeV
python/data_analysis/fermi_lat/vlad_notebooks/Fermi_1-500GeV
python/data_analysis/fermi_lat/vlad_notebooks/Fermi_10_500GeV
python/data_analysis/fermi_lat/vlad_notebooks/Fermi_3_500GeV
python/data_analysis/fermi_lat/vlad_notebooks/Fermi_5_500GeV
python/data_analysis/fermi_lat/vlad_notebooks/Fermi_7_500GeV
python/data_analysis/output_1GeV_15deg_PSF1-3_GAL_old_try
python/data_analysis/output_sgr_0.2GeV_15deg_ALL_old_try
python/sgr1900/results
```

Each path above now exists in the repository as a symbolic link to:

```text
/Users/vdk/software/my_codebase_data/<same-relative-path>
```

Nested Git repositories moved outside the parent repository:

```text
python/projects/detector-simulator
python/projects/fetch-them-all
```

Each nested repository path now exists in the parent repository as a symbolic
link to:

```text
/Users/vdk/software/my_codebase_external_repos/<same-relative-path>
```

The repository also has `.gitignore` rules for large generated artifacts such as
FITS files, HDF5 files, Keras checkpoints, tar/zip archives, generated analysis
output directories, and local caches.
