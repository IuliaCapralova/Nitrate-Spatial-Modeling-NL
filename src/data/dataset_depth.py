import os
import re
import csv
import fiona
import numpy as np
import pandas as pd
import geopandas as gpd
from datetime import datetime
import xml.etree.ElementTree as ET
from dataset_bro import Dataset_BRO


class Dataset_Depth(Dataset_BRO):
    # define columns in new dataframe
    COLUMNS = ["Well_ID","BRO-ID","Filter","Date","Depth","geometry","Ground Level","Bottom Screen","Top Screen"]

    def __init__(self, province, max_files=None) -> None:
        super().__init__(province, type_of_data="well_depth_data", max_files=max_files)

        # parse all XML into a small lookup
        xml_df = self._extract_xml_metadata().set_index("Well_ID") # may be problematic!!

        # build the CSV-timeseries + geometry
        raw = self._extract_data()

        # now map in the XML fields
        for fld in ["Ground Level","Bottom Screen","Top Screen"]:
            raw[fld] = raw["Well_ID"].map(xml_df[fld])

        self._dataframe = raw

    def _extract_data(self) -> pd.DataFrame:
        batches = []
        # start empty
        groundwater_df = pd.DataFrame(columns=self.COLUMNS)

        for path in self._datapaths:
            recs = self._filter_file(path)
            if not recs:
                continue

            # if filter_file returned a single dict, wrap it
            if isinstance(recs, dict):
                recs = [recs]

            # # now recs is guaranteed to be a list of dicts
            # batch = pd.DataFrame.from_records(recs, columns=self.COLUMNS)
            # if batch is not None and not batch.empty:
            #     groundwater_df = pd.concat([groundwater_df, batch], ignore_index=True)


            batch = pd.DataFrame.from_records(recs, columns=self.COLUMNS)
            if not batch.empty:
                batches.append(batch)

        if batches:
            # this concat has no “all-NA” seed frame to worry about
            groundwater_df = pd.concat(batches, ignore_index=True)
        else:
            # no data at all → return the empty schema
            groundwater_df = pd.DataFrame(columns=self.COLUMNS)

        # then attach geometry and XML fields…
        loc = self._location_df_creator()[['Well_ID','geometry']]
        loc = loc.drop_duplicates(subset='Well_ID')
        loc = loc.set_index('Well_ID')
        groundwater_df['geometry'] = groundwater_df['Well_ID'].map(loc['geometry'])

        return groundwater_df

    def _filter_file(self, file_path: str):
        rows = self._read_csv_rows(file_path)

        # --- 1) metadata check ---
        bro_id, raw_date = self._extract_metadata(rows)
        if not bro_id or not raw_date:
            return None

        # "(YYYY-MM-DD, …)" → "YYYY-MM-DD"
        try:
            date_str = raw_date.split(",")[0].strip("() ")
            date_to_check = datetime.strptime(date_str, "%Y-%m-%d")
        except Exception:
            return None

        if date_to_check.year < 2000:
            return None

        # --- 2) extract static fields ---
        well_id, filter_no = self._extract_well_and_filter(rows)

        # --- 3) find the measurement table and collect all rows ---
        recs = []
        for idx, row in enumerate(rows):
            if row and row[0].strip().lower() == "tijdstip meting":
                # determine which columns
                hdr_lower = [c.strip().lower() for c in row]
                di = hdr_lower.index("tijdstip meting")
                wi = hdr_lower.index("waterstand")

                # walk until blank
                for data_row in rows[idx+1:]:
                    if not data_row or not data_row[0].strip():
                        break

                    raw_date = data_row[di]
                    raw_depth = data_row[wi]

                    # parse ISO timestamp (with +HH:MM) if possible
                    try:
                        timestamp = datetime.fromisoformat(raw_date)
                    except Exception:
                        timestamp = raw_date

                    try:
                        depth = float(raw_depth)
                    except Exception:
                        depth = np.nan

                    recs.append({
                        "Well_ID":       well_id,
                        "BRO-ID":        bro_id,
                        "Filter":        filter_no,
                        "Date":          timestamp,
                        "Depth":         depth,
                        "Top Screen":    np.nan,
                        "Bottom Screen": np.nan,
                        "Elevation":     np.nan
                    })
                break

        return recs if recs else None
    
    def _extract_metadata(self, rows):
        header0 = rows[0]
        meta = rows[1] if len(rows)>1 else []
        meta_map = dict(zip(header0, meta))
        return (
            meta_map.get("BRO-ID",    np.nan),
            meta_map.get("datum recentste meting", np.nan)
        )

    def _extract_well_and_filter(self, rows):
        """
        Scan for the 'put BRO-ID' / 'put buisnummer' header row,
        then read the very next row’s corresponding cells.
        Returns (well_id, filter_no), or (None, None) if anything is missing.
        """
        for i, row in enumerate(rows):
            if row and row[0].strip().lower() == "put bro-id":
                # normalize header names
                header = [c.strip().lower() for c in row]
                try:
                    idx_well = header.index("put bro-id")
                    idx_filter = header.index("put buisnummer")
                except ValueError:
                    # header row doesn’t contain both columns
                    return (None, None)

                vals = rows[i + 1] if i + 1 < len(rows) else []
                well_id = vals[idx_well] if idx_well < len(vals) else None
                filter_no = vals[idx_filter] if idx_filter < len(vals) else None

                return (well_id, filter_no)

        # never found the table at all
        return (None, None)
    
    def _extract_xml_metadata(self) -> pd.DataFrame:
        """
        Walk .xml files and pull out:
          - well id
          - longitude, latitude
          - ground Level Position
          - (top, bottom) screen
        """
        namespace = {
            "dsgmw":    "http://www.broservices.nl/xsd/dsgmw/1.1",
            "brocom":   "http://www.broservices.nl/xsd/brocommon/3.0",
            "gmwcommon":"http://www.broservices.nl/xsd/gmwcommon/1.1",
            "gml":      "http://www.opengis.net/gml/3.2"
        }

        records = []
        for path in self.xml_files:
            tree = ET.parse(path)
            root = tree.getroot()

            # 1) Well_ID from <broId>
            wid_el = root.find(".//brocom:broId", namespace)
            well_id = wid_el.text if wid_el is not None else None

            # # 1) BRO-ID
            # bro_id_el = root.find(".//brocom:broId",namespace)
            # bro_id = bro_id_el.text if bro_id_el is not None else None

            # # 2) lon/lat from standardizedLocation → gml:pos "lat lon"
            # pos_el = root.find(
            #     ".//dsgmw:standardizedLocation/brocom:location/gml:pos",
            # namespace
            # )
            # if pos_el is not None:
            #     lat_str, lon_str = pos_el.text.split()
            #     latitude = float(lat_str)
            #     longitude = float(lon_str)
            # else:
            #     latitude = longitude = None

            # 3) ground level
            gl_el = root.find(
                ".//dsgmw:deliveredVerticalPosition/gmwcommon:groundLevelPosition",
            namespace)

            if gl_el is not None and gl_el.text is not None:
                ground_level = float(gl_el.text)
            else:
                ground_level = None

            # 4) top & bottom screen
            screen = root.find(".//dsgmw:monitoringTube/dsgmw:screen", namespace)
            if screen is not None:
                top_el = screen.find("dsgmw:screenTopPosition", namespace)
                bot_el = screen.find("dsgmw:screenBottomPosition",namespace)
                top_screen = float(top_el.text) if top_el is not None else None
                bottom_screen = float(bot_el.text) if bot_el is not None else None
            else:
                top_screen = bottom_screen = None

            records.append({
                "Well_ID":        well_id,
                # "Longitude":     longitude,
                # "Latitude":      latitude,
                "Ground Level":  ground_level,
                "Top Screen":    top_screen,
                "Bottom Screen": bottom_screen
            })

        return pd.DataFrame.from_records(records)
    
    def _location_df_creator(self) -> gpd.GeoDataFrame:
        combined_loc = gpd.GeoDataFrame(columns=["Well_ID", "geometry"])

        for path in self._location_files:
            try:
                layers = fiona.listlayers(path)
                for layer in layers:
                    gdf = gpd.read_file(path, driver="KML", layer=layer)
                    # Select only rows where Name ends with .xml
                    gdf_xml = gdf[gdf["Name"].str.endswith(".xml", na=False)].copy()
                    if not gdf_xml.empty:
                        # Remove '.xml' from Name to get Well_ID
                        gdf_xml["Well_ID"] = gdf_xml["Name"].str.replace(".xml", "", regex=False)
                        gdf_xml = gdf_xml[["Well_ID", "geometry"]] #keep only Well_ID and geometry

                        combined_loc = pd.concat([combined_loc, gdf_xml], ignore_index=True)

            except Exception as e:
                print(f"Failed to load {path}: {e}")

        return combined_loc

if __name__ == "__main__":
    pass
