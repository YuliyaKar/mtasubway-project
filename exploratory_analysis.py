from wrangling import *

def load_data(turnstile_filename, weather_filename):
  """
     This function loads data using preprocessing from wrangling.py file.
     It returns two dataframes: weather_data and turnstile_data.

     Parameters
     ----------
     master_filename: path to turnstile csv file,
                      containing [C/A,UNIT,SCP,DATEn,TIMEn,DESCn,ENTRIESn,EXITSn]
                      columns.
     weather_filename: path to weather data.

    Returns
    --------
    turnstile: Pandas DataFrame with turnstile preprocessed data.
    weather: Pandas DataFrame with weather data.
  """

  turnstile = filter_by_regular(turnstile_filename)
  turnstile = get_hourly_exits(turnstile)
  turnstile = get_hourly_entries(turnstile)

  turnstile['HOUR'] = turnstile.TIMEn.apply(time_to_hour)
  turnstile['DATEn'] = turnstile.DATEn.apply(reformat_subway_dates)

  weather = pd.read_csv(weather_filename)

  return turnstile, weather

def merge_turnstile_weather(turn, weath):
    """
        Merge 2 dataframes to a single one on date.
    """
    weath = weath.rename(columns={'date': 'DATEn'})
    data = pd.merge(turn, weath, on=['DATEn'], how='inner')

    return data
