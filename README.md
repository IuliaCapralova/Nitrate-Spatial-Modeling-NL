# Bachelor-Thesis

This project aims to analyze **nitrate leaching** in the Netherlands using **machine learning techniques**. At this stage, the focus is on **exploratory data analysis (EDA)**, bringing together various spatial and chemical datasets to understand the patterns and features relevant for predictive modeling.

---

### Data Overview

The data used in this project includes several types of environmental information. We have soil maps that show different areas of land with details about the layers of soil underneath. There are also measurements of groundwater depth taken at specific locations. The chemical composition of the soil is available too, showing the amount of elements like barium, aluminum, sulfur, and silicon at different depths from borehole samples. In addition, we use a land use map (LGN7) that shows how the land is being used across the country, such as for farming, nature, or urban areas. Lastly, we have the exact locations where samples were collected, stored in files with coordinates.

## Repository Structure

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


To run the notebooks, you’ll need the following Python packages:

pip install geopandas rioxarray rasterio contextily osmnx fiona shapely xarray seaborn datashader rasterstats
