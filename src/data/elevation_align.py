import os
import requests
import time
import pandas as pd
from align_data import BaseAligner


class ElevationAligner(BaseAligner):
    def __init__(self, well_filter=1, api_key="AIzaSyBcDtNXhWW-NmOu3CYxs06-AqwfxhLS_OY"):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")  # allow API key as arg or env var
        super().__init__(well_filter)
        self._dataframe = self._align()

    def _get_google_elevation(self, lat, lon):
        url = f"https://maps.googleapis.com/maps/api/elevation/json?locations={lat},{lon}&key={self.api_key}"
        try:
            response = requests.get(url)
            data = response.json()
            if response.status_code == 200:
                results = response.json().get("results", [])
                if results:
                    return results[0]["elevation"]
            else:
                print(f"HTTP Error {response.status_code}: {data}")
        except Exception as e:
            print(f"Error at ({lat}, {lon}): {e}")
        return None

    def _align(self):
        gdf = self.nitrate_gdf.copy()
        gdf["lon"] = gdf.geometry.x
        gdf["lat"] = gdf.geometry.y

        # Optional: Deduplicate locations to save quota
        coord_to_elev = {}
        for lat, lon in zip(gdf["lat"], gdf["lon"]):
            key = (lat, lon)
            if key not in coord_to_elev:
                coord_to_elev[key] = self._get_google_elevation(lat, lon)
                time.sleep(0.1)  # avoid quota issues

        # Map back to original
        gdf["Elevation_m"] = gdf.apply(lambda row: coord_to_elev.get((row["lat"], row["lon"])), axis=1)
        return gdf


if __name__ == "__main__":
    instance = ElevationAligner(well_filter=1, api_key="AIzaSyBcDtNXhWW-NmOu3CYxs06-AqwfxhLS_OY")
    print(instance._dataframe)
    # aligner = ElevationAligner(well_filter=1, api_key="AIzaSyBcDtNXhWW-NmOu3CYxs06-AqwfxhLS_OY")
    # print(aligner._get_google_elevation(52.092876, 5.104480))  # Use known coordinates in Utrecht
