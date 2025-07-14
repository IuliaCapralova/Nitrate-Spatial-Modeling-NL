# Spatial Prediction of Nitrate Leaching in North Utrecht

This project aims to analyze **nitrate leaching** in the Netherlands using **machine learning techniques**. At this stage, the focus is on **exploratory data analysis (EDA)**, bringing together various spatial and chemical datasets to understand the patterns and features relevant for predictive modeling.

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


# Project Name

A brief description of your project and its purpose.

---

## ▼ Table of Contents

1. [About The Project](#about-the-project)
    - [Built With](#built-with)
2. [Getting Started](#getting-started)
    - [Dependencies](#dependencies)
    - [Installation](#installation)
3. [Usage](#usage)
4. [Roadmap](#roadmap)
5. [Contributing](#contributing)
6. [License](#license)
7. [Authors](#authors)
8. [Acknowledgements](#acknowledgements)

---

## About The Project

Describe what your project does and why it exists.

### Built With

- [Tech1](#)
- [Tech2](#)
- [Tech3](#)

---

## Getting Started

Simple instructions to get your project up and running.

### Dependencies

- Dependency 1
- Dependency 2

### Installation

```bash
# Step 1
command_to_install

# Step 2
another_command
