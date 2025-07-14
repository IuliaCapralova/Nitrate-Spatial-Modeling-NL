# Spatial Prediction of Nitrate Leaching in North Utrecht

This project analyze **nitrate leaching** in the Netherlands using **machine learning techniques**. At this stage, the focus is on **exploratory data analysis (EDA)**, bringing together various spatial and chemical datasets to understand the patterns and features relevant for predictive modeling.

---

### Data Overview

The data used in this project includes several types of environmental information. We have soil maps that show different areas of land with details about the layers of soil underneath. There are also measurements of groundwater depth taken at specific locations. The chemical composition of the soil is available too, showing the amount of elements like barium, aluminum, sulfur, and silicon at different depths from borehole samples. In addition, we use a land use map (LGN7) that shows how the land is being used across the country, such as for farming, nature, or urban areas. Lastly, we have the exact locations where samples were collected, stored in files with coordinates.

## Repository Structure

```
.
├── data
│   ├── LGN7_land_use
│   ├── soil_chem_data
│   ├── type_of_soil_data
│   ├── Wageningen_soil_map
│   └── Wageningen_water_data
├── notebooks
│   ├── Data_exploration_soil_map.ipynb
│   ├── Data_exploration_water_map.ipynb
│   └── soil_chem_composition.ipynb
├── README.md
├── results
└── src
```


All package dependencies can be found in the requirements.txt file

To run code regarding data, please ensure you are in src folder, then run the following:

python data/main.py




---


# Explainable Spatial Modeling of Groundwater Nitrate Concentrations in the Netherlands

---

## ▼ Table of Contents

1. [About The Project](#about-the-project)
2. [Getting Started](#getting-started)
    - [Installation](#installation)
    - [Dependencies](#dependencies)
    - [Repository Structure](#repository_structure)
    - [Data Folder setup](#folder_setup)
3. [Usage](#usage)
4. [Roadmap](#roadmap)
5. [Contributing](#contributing)
6. [License](#license)
7. [Authors](#authors)
8. [Acknowledgements](#acknowledgements)

---

## About The Project

This project creates a spatial regression map for nitrate leaching across the entire territory of the Netherlands. Nitrate leaching from agricultural soils is a major driver of groundwater pollution, especially in regions with intensive farming. Since nitrate measurements are limited to a few monitoring sites, there’s a need for interpretable, data-driven models that can predict nitrate concentrations nationwide.

Here, an explainable spatial regression model is developed using spatial and environmental data from Dutch agricultural soils. The approach benchmarks Ridge Regression, Random Forest, and XGBoost models, ultimately combining Random Forest and XGBoost in an ensemble. The workflow also applies model-specific and model-agnostic interpretability methods (SHAP, LIME Permutation) to reveal key factors behind nitrate leaching.

The resulting maps visualize how nitrate pollution has changed between 2010 and 2023, and help identify regions where concentrations remain high. This project is designed to support decision-making for localized policies aimed at reducing nitrate leaching.

---

## Getting Started

The following sections explain how to set up the project and run it locally.

### Installation

Clone the repo:
```bash
https://github.com/IuliaCapralova/Bachelor-Thesis.git
```

### Dependencies

Before getting started, make sure you have right Python version:

* Python 3.9.6

Next, a project environment should be created. Follow the steps:

1. Navigate to the project root directory:

```bash
cd Bachelor-Thesis
```

2. Create a virtual environment:
```bash
python3 -m venv spatial_env
```

3. Activate the virtual environment:
```bash
source spatial_env/bin/activate
```

4. Install all required dependencies:
```bash
pip install -r requirements.txt
```
This will install all necessary packages for running the spatial modeling and prediction pipeline.

### Repository Structure

Bachelor-Thesis/
├── data/                 # Raw, cleaned, and aligned spatial and environmental datasets
├── logging/              # Logging configuration and saved logs for pipeline runs
├── notebooks/            # Jupyter notebooks for exploratory analysis and model experimentation
├── plots/                # Final visualizations used in the thesis and report
├── r_scrips_plots/       # R scripts used for generating plots
├── requirements.txt      # List of all Python packages required to run the project
├── src/                  # Source code: preprocessing, training, prediction, evaluation modules
├── trained_models/       # Saved machine learning models (.pkl)
├── README.md             # Project overview and setup instructions



### Data Folder setup

Next, a `data` folder should be created separately in the root of the repository `Bachelor-Thesis`.
It contains all raw, clean, and aligned input datasets used in the modeling pipeline. The folder
set up should be as follows:

```bash
data/
├── aligned/
│   ├── aligned_grid_2023/
│   ├── aligned_grid_2021/
│   ├── aligned_grid_2017/
│   └── aligned_grid_2010/
│
├── clean/
│   ├── elevation/
│   ├── environment/
│   ├── land_use/
│   ├── n_deposition/
│   ├── population_density/
│   ├── soil_composition/
│   ├── type_of_soil/
│   ├── well_chem_data/
│   └── well_depth_data/
│
├── grids_for_prediction/
│
├── raw/
│   ├── well_depth_data/
│   ├── population_density/
│   ├── well_chem_data/
│   ├── provinces_nl/
│   ├── soil_composition/
│   ├── soil_chem_data/
│   ├── n_deposition/
│   ├── type_of_soil_data/
│   ├── land_use/
│   └── type_of_soil/
```

## Usage

To run a preprocessing pypeling run the following:

```bash
python3 src/data/main.py
```
In the `main.py` follow the instractions regarding provinces, features, and years of interest. Adjust it for your needs.

To run a preprocessing pypeling run the following:

```bash
python3 src/model/main.py
```
