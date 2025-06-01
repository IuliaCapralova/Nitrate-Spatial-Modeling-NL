import pandas as pd
from datetime import datetime, timedelta
from knmy.knmy import get_daily_data


class Environmental_Preprocess():
    def __init__(self, station_id=260, start_date="20120101", end_date="20201231", variables=['TEMP', 'PRCP']) -> None:
        # Due to future alignment the start date should be modified
        start_date_dt = datetime.strptime(start_date, "%Y%m%d") - timedelta(days=60)
        adjusted_start = start_date_dt.strftime("%Y%m%d")

        _, _, _, weather_df = get_daily_data(
            stations=[station_id],
            start=adjusted_start,
            end=end_date,
            variables=variables,
            parse=True
        )
        self._dataframe = self._clean(weather_df)

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

    def __getitem__(self, idx):
        return self._dataframe.iloc[idx]

    def __len__(self):
        return len(self._dataframe)


if __name__ == "__main__":
    start_date = "20120101"
    end_date = "20201231"
    instance = Environmental_Preprocess()
    print(instance._dataframe)
