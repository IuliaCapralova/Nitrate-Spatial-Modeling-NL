import os
import re
import csv
import fiona
import numpy as np
import pandas as pd
import geopandas as gpd
from dataset_bro import Dataset_BRO


class Dataset_Nitrate(Dataset_BRO):
    # define columns in new dataframe
    COLUMNS = ["Well_ID", "BRO-ID", "Filter", "Date", "Nitrate", "Chloride", "Oxygen", "Temperature", "Acidity"]

    def __init__(self, province, max_files=None) -> None:
        super().__init__(province, type_of_data="well_chem_data", max_files=max_files)

    def _extract_data(self) -> pd.DataFrame:        
        # create DataFrame with columns above
        groundwater_df = pd.DataFrame(columns=self.COLUMNS)

        # extract only water properties
        for path in self._datapaths:
            extracted_row = self._filter_file(path) # from the csv we extract all needed info in one single row
            if extracted_row:
                groundwater_df = pd.concat([groundwater_df, pd.DataFrame([extracted_row])], ignore_index=True) # save this row/s

        # extract and link locations
        location_df = self._location_df_creator()
        groundwater_df = groundwater_df.merge(location_df[['BRO-ID', 'geometry']], on='BRO-ID', how='left')

        return groundwater_df

    def _filter_file(self, file_path:str) -> dict:
        rows = self._read_csv_rows(file_path)
        bro_id, date, buis = self._extract_metadata(rows)
        well_id = self._extract_well_id(file_path)

        # 3) set up the output
        output = {
            "Well_ID":    well_id,
            "BRO-ID":     bro_id,
            "Filter":     buis,
            "Date":       date,
            "Nitrate":    np.nan,
            "Chloride":   np.nan,
            "Oxygen":     np.nan,
            "Temperature":np.nan,
            "Acidity":    np.nan
        }

        # 4) what we’re looking for
        wanted = {
          "Nitrate":    "nitraat",
          "Chloride":   "chloride",
          "Oxygen":     "zuurstof",
          "Temperature":"temperatuur",
          "Acidity":    "zuurgraad",
        }

        # 5) scan for “parameter” tables
        i = 0
        while i < len(rows):

            row = rows[i]
            if row and row[0].strip().lower() == "parameter":
                header_row = row
            
                # find first real data row
                first_data = self._find_first_data_row(rows, i + 1)
                if first_data is None:
                    break

                val_col = self._detect_value_column(header_row, first_data)
                if val_col is not None:
                    # pull out each wanted parameter from this block
                    output = self._popuplate_output_from_table(rows, first_data_idx=i+1, val_col=val_col, wanted=wanted, output=output)

                # move past this table
                i = self._skip_past_table(rows, i + 1)
            else:
                i = i + 1

        return output

    def _extract_metadata(self, rows):
        header0 = rows[0]
        meta = rows[1] if len(rows)>1 else []
        meta_map = dict(zip(header0, meta))
        return (
            meta_map.get("BRO-ID",    np.nan),
            meta_map.get("tijdstip veldonderzoek", np.nan),
            meta_map.get("buis", np.nan),
        )
    
    def _extract_well_id(self, file_path):
        for part in os.path.normpath(file_path).split(os.sep):
            match = re.match(r"GMW\w+", part)
            if match:
                return match.group(0)
        return None

    def _find_first_data_row(self, rows, start_idx):
        """Skip blanks and return first non‑empty row after a header."""
        for idx in range(start_idx, len(rows)):
            #skip empty rows or rows whose first cell is empty
            if rows[idx] and rows[idx][0].strip():
                return rows[idx]
        return None

    def _detect_value_column(self, header_row, first_data_row):
        """
        Look across header_row for the first column that contains
        a float in first_data_row but isn’t one of the metadata columns.
        """
        skip_keys = ("parameter","sikb","aquo-code","analysedatum","eenheid meerwaarde", "rapportagegrens", "eenheid rapportagegres", "limietsymbool", "status kwaliteitscontrole")
        for j, colname in enumerate(header_row):
            lc = colname.lower()
            if any(sk in lc for sk in skip_keys):
                continue
            try:
                float(first_data_row[j])
                return j
            except Exception:
                continue
        return None

    def _popuplate_output_from_table(self, rows, first_data_idx, val_col, wanted, output):
        """
        Walk rows from first_data_idx until the next blank or next 'parameter',
        pulling out any wanted parameters into output.
        """
        # loop until first cell of the row is not equal to "parameter" (bcs this is a start of new table)
        while first_data_idx < len(rows) and rows[first_data_idx] and rows[first_data_idx][0].strip().lower() != "parameter":
            # check if the first cell of the row is equal to the attribute we are looking for
            variable_name = rows[first_data_idx][0].strip().lower()
            for out_key, label in wanted.items():
                if variable_name == label and len(rows[first_data_idx]) > val_col:
                    output[out_key] = rows[first_data_idx][val_col].strip()
            first_data_idx += 1
        return output

    def _skip_past_table(self, rows, idx):
        """
        Return the index just after this block of data rows, so the
        main loop can look for the next table header.
        """
        while idx < len(rows) and rows[idx] and rows[idx][0].strip().lower() != "parameter":
            idx += 1
        return idx
    
    def _location_df_creator(self) -> gpd.GeoDataFrame:
        # Go in each province folder
        # Each region folder
        # Find "locatie_levering.kml"
        # Add all of them up
        # Read one by one, add each feature in each layer in geo table
        combined_loc = gpd.GeoDataFrame()

        for path in self._location_files:
            try:
                layers = fiona.listlayers(path)
                for layer in layers:
                    gdf = gpd.read_file(path, driver="KML", layer=layer)
                    gdf["source_layer"] = layer
                    combined_loc = pd.concat([combined_loc, gdf], ignore_index=True)
            except Exception as e:
                print(f"Failed to load {path}: {e}")
        #rename column
        combined_loc['BRO-ID'] = combined_loc['Name'].str.replace('.csv', '', regex=False)
        return combined_loc

    def get_df(self) -> pd.DataFrame:
        """
        Returns dataset as a DataFrame.
        """
        return self._dataframe
    
    # TODO
    def __getitem__(self):
        """
        Access the file from df at a given index.
        """
        pass

    # TODO
    def __len__(self):
        """
        Return the number of collected CSV files.
        """
        pass
    

if __name__ == "__main__":
    well_chem_data = Dataset_Nitrate(province="utrecht", type_of_data = "well_chem_data")
    full_df = well_chem_data._dataframe
    print(full_df.head())
