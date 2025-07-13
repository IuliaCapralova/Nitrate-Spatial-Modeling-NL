import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import numpy as np
import os
from datetime import datetime, timezone

def generate_empty_grid(provinces: list, years: int, month: str, day: str, resolution_m: int = 500):

    print(f"Generating empty grid for year {years}, provinces: {provinces}")

    curr_dir = os.getcwd()
    provinces_path = os.path.join(curr_dir, "../data/raw/provinces_nl", "BestuurlijkeGebieden_2025.gpkg")
    
    # Load province layer and select relevant ones
    gdf = gpd.read_file(provinces_path, layer="provinciegebied")
    gdf["naam"] = gdf["naam"].str.lower()
    gdf = gdf[gdf["naam"].isin(provinces)]

    gdf = gdf.to_crs(epsg=28992)

    bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
    minx, miny, maxx, maxy = bounds

    # Create the grid
    x_coords = np.arange(minx, maxx, resolution_m)
    y_coords = np.arange(miny, maxy, resolution_m)

    points = []
    for x in x_coords:
        for y in y_coords:
            point = Point(x + resolution_m / 2, y + resolution_m / 2)
            points.append(point)

    grid_gdf = gpd.GeoDataFrame(geometry=points, crs="EPSG:28992")

    # Clip grid to selected provinces
    grid_gdf = gpd.overlay(grid_gdf, gdf, how='intersection')

    # Reproject back to EPSG:4326
    grid_gdf = grid_gdf.to_crs(epsg=4326)

    # Add date and year
    date = pd.Timestamp(f"{years}-{month}-{day} 10:00:00", tz=timezone.utc)
    grid_gdf["date"] = date
    grid_gdf["Year"] = years

    # Keep only relevant columns
    grid_gdf = grid_gdf[["geometry", "date", "Year"]]

    return grid_gdf


if __name__ == "__main__":
    provinces = ["utrecht", "flevoland", "noord-holland", "zuid-holland"]
    # provinces = ["utrecht"]
    years = [2010]

    grid = generate_empty_grid(provinces, years[0])
    print(grid)
