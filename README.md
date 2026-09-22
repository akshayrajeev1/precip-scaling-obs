# Spatial and temporal scaling of precipitation using observations

This repository contains data, code, and analysis for the observation-based study:
**"Dependence of the precipitation intensity distribution on spatial and temporal resolution in observations"**

It focuses on merged satellite-derived and station-based precipitation datasets to explore how increasing spatial and temporal resolution influences rain amount distributions.

## Folder Structure

```
.
├── data/               # Processed data for plotting (rain amount distributions, direct modes of change etc.)
├── notebooks/          # Jupyter notebooks for visualization of results
├── scripts/            # Python scripts for processing and analysis
├── figs/               # Figures used in the publication
```

## Getting Started

```bash
git clone https://github.com/akshayrajeev1/precip-scaling-obs.git
cd precip-scaling-obs
conda env create -f environment.yml
conda activate prec-res
```

## Datasets Used

- **IMERG Final Run V07B** (0.1° resolution): [GPM NASA Website](https://gpm.nasa.gov/)
- **FROGS Database** (1° resolution): [FROGS website](https://frogs.ipsl.fr)
- **In-situ observations** (1-minute resolution): [US DOE Atmospheric Radiation Measurement (ARM) program](https://armgov.svcs.arm.gov/data)


## Key Analyses

- Spatial coarsening and temporal aggregation
- Construction of precipitation amount distribution at different spatial and temporal resolutions
- Construction of the joint precipitation amount distribution at different spatial and temporal resolutions
- Estimate the shift of the precipitation amount distributions between spatial resolutions using the shift mode
- Spatial distribution of the shift mode
- Estimate the shift of the precipitation amount distributions between temporal resolutions using the shift mode.

## Citation

> Rajeev, Masleyev and Pendergrass (In Prep). "Observed spatial and temporal scaling of the intensity distribution of precipitation".
