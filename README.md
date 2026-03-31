# Spatial and temporal scaling of precipitation using observations

This repository contains data, code, and analysis for the observation-based study:
**"Observed spatial and temporal scaling of the intensity distribution of Precipitation"**

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
git clone https://github.com/akshayrajeev1/scaling-precip-obs.git
cd precip-resolution-obs
conda env create -f environment.yml
conda activate scaling
```

## Datasets Used

- **IMERG Final Run V07B** (0.1° resolution): [GPM NASA Website](https://gpm.nasa.gov/)
- **FROGS Database** (1° resolution): [FROGS website](https://frogs.ipsl.fr)


## Key Analyses

- Spatial coarsening and temporal aggregation
- Construction of rain amount distribution
- Construction of the joint rain amount distribution
- Estimate the shift in rain rates using the shift mode.
- Spatial distribution of the shift mode
- Temporal scaling of precipitation using station data

## Citation

> Rajeev, Masleyev and Pendergrass (In Prep). "Observed spatial and temporal scaling of the intensity distribution of precipitation".
