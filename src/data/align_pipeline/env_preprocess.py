import os
import pandas as pd
from typing import List, Union
from datetime import datetime, timedelta
from knmy.knmy import get_daily_data

# try:
#     from ..dataset_saver import Dataset_Saver
# except ImportError:
#     from dataset_saver import Dataset_Saver


class Environmental_Preprocess():
    def __init__(self, station_ids:List[int]=None, start_date:str="20080101", end_date:str="20231231", variables=['TEMP', 'PRCP']) -> None:
        self._dataframe = {}
        self.start_date = start_date
        self.end_date = end_date
        self.variables = variables
    
    def __call__(self, station_ids: Union[int, List[int]]):
        if isinstance(station_ids, int):
            station_ids = [station_ids]

        # Due to future alignment the start date should be modified
        start_date_dt = datetime.strptime(self.start_date, "%Y%m%d") - timedelta(days=60)
        adjusted_start = start_date_dt.strftime("%Y%m%d")

        for station_id in station_ids:
            print(f"Fetching data for station {station_id}...")
            df = self._fetch_station_data(station_id, adjusted_start, self.end_date, self.variables)

            if df is not None:
                clean_df = self._clean(df)   # clean before adding to dict
                self._dataframe[station_id] = clean_df

        # Save newly created dataframe
        print(self._dataframe)
        self._save()

    def _fetch_station_data(self, station_id, adjusted_start, end_date, variables):
        try:
            _, _, _, df = get_daily_data(
                stations=[station_id],
                start=adjusted_start,
                end=end_date,
                variables=variables,
                parse=True
            )
            # add extra info about station used
            df['station'] = station_id
            return df

        except Exception as e:
            print(f"Failed for station {station_id}: {e}")
            return None

    def _clean(self, df):
        df['Date'] = pd.to_datetime(df['YYYYMMDD'], format='%Y%m%d')
        df = df.drop(columns=['YYYYMMDD', 'TN', 'TX', 'T10N', 'DR', 'EV24'], errors='ignore')
        df = df.rename(columns={
            'STN': 'station',
            'TG': 'temp_mean',
            'RH': 'precip_sum'
        })

        if 'precip_sum' in df.columns:
            df['precip_sum'] = df['precip_sum'].replace(-1, 0)  # when -1 values is <0.05 mm

        return df
    
    def _save(self):
        from dataset_saver import Dataset_Saver  # deferred import
        saver = Dataset_Saver()
        curr_dir = os.getcwd()
        save_dir = os.path.join(curr_dir, "../data/clean/environment")

        os.makedirs(save_dir, exist_ok=True)
        saver(self, save_dir)

        print(f"METEO data is successfully preprocessed and saved!")

    def __getitem__(self, idx):
        return self._dataframe.iloc[idx]

    def __len__(self):
        return len(self._dataframe)
    
    @property
    def dataframe(self):
        return self._dataframe


if __name__ == "__main__":
    provinces = ["utrecht", "flevoland"]
    start_date = "20080101"
    end_date = "20231231"
    instance = Environmental_Preprocess(provinces, start_date="20080101", end_date="20231231", variables=['TEMP', 'PRCP'])
    print(instance.dataframe)
