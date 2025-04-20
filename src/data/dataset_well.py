import os
import pandas as pd
import numpy as np
import csv
import re
from pathlib import Path
from abc import ABC, abstractmethod
from dataset import DataSet

class Dataset_Well(DataSet):
    def __init__(self, type_of_data = "well_chem_data", type_of_file = ".csv") -> None:
        super().__init__(type_of_data="well_chem_data", type_of_file=".csv")

        self._dataframe = self._extract_data()

    
    def _extract_data(self) -> pd.DataFrame:
        # define columns in new dataframe
        columns = ["Well_ID", "BRO-ID", "Date", "Nitrate", "Chloride", "Oxygen", "Temperature", "Acidity"]
        # columns = ["Well_ID", "BroID", "analysedatum", "nitraat", "fosfaat", "Temperatuur", "Zuurgraad"]

        # create DataFrame with columns above
        groundwater_df = pd.DataFrame(columns=columns)

        for path in self._datafiles:
            sample_csv_df = pd.read_csv(path)
            extracted_row = self._filter_file(sample_csv_df, path) # from the csv we extract all needed info in one single row
            groundwater_df = pd.concat([groundwater_df, pd.DataFrame([extracted_row])], ignore_index=True) # save this row

        return groundwater_df
        

    # def _filter_file(self, sample_csv_df:pd.DataFrame, file_path:str) -> dict:

    #     # For each row in the new dataframe save the following columns and correspoinding info:

    #     # Bro_id: The 0-th row under "BRO-ID" column
    #     # Date: The 0-th row under "tijdstip veldonderzoek" column
    #     # Oxygen (zuurstof): Under "BRO-ID" find "zuurstof", in this row, in the fourth column will be the value - save it.
    #     # Temperature (Temperatuur): In this row, fourth column - save the value
    #     # Acidity (Zuurgraad): Again, in this row, fourth column - save the value
    #     # Nitrate (nitraat): Under "BRO-ID" find "nitraat", in this row find fifth column and save the value
    #     # Chloride (chloride): same as Nitrate
        
    #     # extract Bro ID and Date
    #     metadata_row = sample_csv_df.iloc[0]
    #     bro_id = metadata_row["BRO-ID"] if "BRO-ID" in sample_csv_df.columns else np.nan
    #     date = metadata_row["tijdstip veldonderzoek"] if "tijdstip veldonderzoek" in sample_csv_df.columns else np.nan

    #     # extract well ID
    #     well_id = None
    #     folder_parts = os.path.normpath(file_path).split(os.sep)
    #     for part in folder_parts:
    #         match = re.match(r"GMW\w+", part)
    #         if match:
    #             well_id = match.group(0)
    #             break


    #     # filename = os.path.basename(file_path)
    #     # well_id_match = re.search(r"GMW\w+", filename)
    #     # well_id = well_id_match.group(0) if well_id_match else None

    #     extracted_row = {
    #         "Well_ID": well_id,
    #         "BRO-ID": bro_id,
    #         "Date": date,
    #         "Nitrate": np.nan,
    #         "Chloride": np.nan,
    #         "Oxygen": np.nan,
    #         "Temperature": np.nan,
    #         "Acidity": np.nan
    #     }

        
    #     # way to find where the value is for the attributes
    #     parameters = {
    #     "Oxygen": ("zuurstof", 3),
    #     "Temperature": ("Temperatuur", 3),
    #     "Acidity": ("Zuurgraad", 3),
    #     "Nitrate": ("nitraat", 4),
    #     "Chloride": ("chloride", 4)
    #     }

    #     bro_id_column = "BRO-ID"
    #     if bro_id_column in sample_csv_df.columns:

    #         # loop through each (index, value) pair in the BRO-ID column
    #         for i, value in sample_csv_df[bro_id_column].items():
    #             if pd.isna(value):
    #                 continue

    #             # check if we have specific names under "BRO-ID" column
    #             # and if we do save the value from that row but another column
    #             for key, (param_label, col_index) in parameters.items():
    #                 if value.strip().lower() == param_label.lower():
    #                     try:
    #                         extracted_row[key] = sample_csv_df.iloc[i, col_index]
    #                     except Exception:
    #                         extracted_row[key] = np.nan

    #     return extracted_row


    def _filter_file(self, file_path:str) -> dict:
        # we ignore pandas here and read raw CSV
        rows = []
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)

        # 1) metadata
        header0 = rows[0]
        meta    = rows[1] if len(rows)>1 else []
        meta_map = dict(zip(header0, meta))
        bro_id = meta_map.get("BRO-ID",    np.nan)
        date   = meta_map.get("tijdstip veldonderzoek", np.nan)

        # 2) well‐ID from folder name
        well_id = None
        for part in os.path.normpath(file_path).split(os.sep):
            m = re.match(r"GMW\w+", part)
            if m:
                well_id = m.group(0)
                break

        # 3) set up our output
        output = {
            "Well_ID":    well_id,
            "BRO-ID":     bro_id,
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
            # find the next parameter‐table header
            i = self._find_next_table_header(rows, i)
            if i is None:
                break

            header_row = rows[i]
            first_data = self._find_first_data_row(rows, i + 1)
            if first_data is None:
                break

            val_col = self._detect_value_column(header_row, first_data)
            if val_col is not None:
                # pull out each wanted parameter from this block
                self._popuplate_output_from_table(rows, first_data_idx=i+1, val_col=val_col, wanted=wanted, output=output)

            # move past this table
            i = self._skip_past_table(rows, i + 1)

        return output

    def _read_csv_rows(self, path):
        with open(path, newline='', encoding='utf-8') as f:
            return list(csv.reader(f))

    def _extract_metadata(self, rows):
        header0 = rows[0]
        meta    = rows[1] if len(rows)>1 else []
        meta_map = dict(zip(header0, meta))
        return (
            meta_map.get("BRO-ID",    np.nan),
            meta_map.get("tijdstip veldonderzoek", np.nan)
        )

    def _extract_well_id(self, file_path):
        for part in os.path.normpath(file_path).split(os.sep):
            m = re.match(r"GMW\w+", part)
            if m:
                return m.group(0)
        return None

    def _find_next_table_header(self, rows, start_idx):
        """Return index of next row whose first cell == 'parameter', else None."""
        for idx in range(start_idx, len(rows)):
            if rows[idx] and rows[idx][0].strip().lower() == "parameter":
                return idx
        return None

    def _find_first_data_row(self, rows, start_idx):
        """Skip blanks and return first non‑empty row after a header."""
        for idx in range(start_idx, len(rows)):
            if rows[idx] and rows[idx][0].strip():
                return rows[idx]
        return None

    def _detect_value_column(self, header_row, first_data_row):
        """
        Look across header_row for the first column that contains
        a float in first_data_row but isn’t one of the metadata columns.
        """
        skip_keys = ("parameter","sikb","aquo","datum","eenheid")
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
        idx = first_data_idx
        while idx < len(rows) and rows[idx] and rows[idx][0].strip().lower() != "parameter":
            pname = rows[idx][0].strip().lower()
            for out_key, label in wanted.items():
                if pname == label and len(rows[idx]) > val_col:
                    output[out_key] = rows[idx][val_col].strip()
            idx += 1

    def _skip_past_table(self, rows, start_idx):
        """
        Return the index just after this block of data rows, so the
        main loop can look for the next table header.
        """
        idx = start_idx
        while idx < len(rows) and rows[idx] and rows[idx][0].strip().lower() != "parameter":
            idx += 1
        return idx

    def get_df(self) -> pd.DataFrame:
        """
        Returns dataset as a DataFrame.
        """
        return self._dataframe
    

if __name__ == "__main__":
    well_chem_data = Dataset_Well(type_of_data = "well_chem_data", type_of_file = ".csv")
    data = well_chem_data.get_df()
    print(data.head(15))
