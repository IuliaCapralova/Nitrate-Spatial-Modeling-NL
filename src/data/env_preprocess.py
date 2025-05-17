import pandas as pd
from knmy.knmy import get_daily_data


class Environmental_Preprocess():
    def __init__(self, station_id=260, start_date="20120101", end_date="20201231", variables=['TEMP', 'PRCP']) -> None:
        _, _, _, weather_df = get_daily_data(
            stations=[station_id],
            start=start_date,
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
        return df

    def __getitem__(self, idx):
        return self._dataframe.iloc[idx]

    def __len__(self):
        return len(self._dataframe)


if __name__ == "__main__":
    start_date = "20120101"
    end_date = "20201231"
    variables = ['PRCP', 'PRCP']
    instance = Environmental_Preprocess()
    print(instance._dataframe)
