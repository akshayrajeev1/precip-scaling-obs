# Spatial scaling of precipitation – Observational Analysis

This repository contains data, code, and analysis for the observation-based component of the study:
**"Observed spatial scaling of the intensity distribution of rain"**

It focuses on merged satellite-derived precipitation datasets to explore how coarsening spatial resolution influences rainfall amount distributions.

## 📂 Folder Structure

```
.
├── data/               # Processed data for plotting (rain amount distributions, shift map etc.)
├── notebooks/          # Jupyter notebooks for exploratory analysis and visualization
├── scripts/            # Python scripts for processing and statistical analysis
├── figs/               # Figures used in the publication
```

## 📥 Getting Started

```bash
git clone https://github.com/akshayrajeev1/scaling-precip-obs.git
cd scaling-precip-obs
conda env create -f environment.yml
conda activate spatial-scaling
```

## 📜 Datasets Used

- **IMERG Final Run V07** (0.1° resolution): [GPM NASA Website](https://gpm.nasa.gov/)
- **FROGS Database** (1° resolution): [FROGS website](https://frogs.ipsl.fr)


## 📊 Key Analyses

- Spatial coarsening and aggregation
- Construction of rain amount distribution
- Construction of the joint rain amount distribution
- Estimate the shift in rain rates using the shift mode.
- Spatial distribution of the shift mode

## 📄 Citation

> Rajeev and Pendergrass (In Prep). "Observed spatial scaling of the intensity distribution of rain".
