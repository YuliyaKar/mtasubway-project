from wrangling import *
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np

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

def entries_hist(data):
    """
        Plot the frequency of hourly entries depending on
        whether it is rainy day or not.
    """
    fig = plt.figure()

    rainy = data[data['rain'] == 1]['ENTRIESn_hourly']
    nrainy = data[data['rain'] == 0]['ENTRIESn_hourly']

    plt.hist(nrainy, bins=20, range=(0, 4000), label='No Rain', color='blue',
             alpha=0.8, ec='black', ls='solid')
    plt.hist(rainy, bins=20, range=(0, 4000), label='Rain', color='green',
             alpha=0.8, ec='black', ls='solid')

    plt.xlabel('Number of hourly entries')
    plt.ylabel('Frequency')
    plt.legend()

    return fig

def mann_whitney_test_entries(data):
    """
        This function computes the mean number of entries when raining
        and not, and compares two samples using Mann Whitneys test (because data
        are not distributed normally).

        Returns
        ------
        with_rain_mean: Mean number of hourly entries when raining.
        without_rain_mean: Mean number of hourly entries when no rain.
        U: The Mann-Whitney U-statistic.
        p: p-value.
    """

    rainy = data[data['rain'] == 1]['ENTRIESn_hourly']
    nrainy = data[data['rain'] == 0]['ENTRIESn_hourly']

    with_rain_mean = rainy.mean()
    without_rain_mean = nrainy.mean()

    U, p = stats.mannwhitneyu(rainy, nrainy)

    return with_rain_mean, without_rain_mean, U, p


#-----------------
# The following part contains Linear Regression implementation
# with gradient decent for the learning purpose.

def normalize_features(df):
    """
        Normalize features in the data set.
    """
    mu = df.mean()
    sigma = df.std()

    if (sigma == 0).any():
        raise Exception("One or more features had the same value for all samples, and thus could " + \
                         "not be normalized. Please do not include features with only a single value " + \
                         "in your model.")

    df_normalized = (df - mu) / sigma
    return df_normalized, mu, sigma

def compute_cost(features, values, theta):
    """
        Compute the cost function given a set of features /
        values, and the values of thetas.
    """

    m = len(values)
    cost = np.square(np.dot(features, theta) - values).sum() / (2 * m)

    return cost

def gradient_descent(features, values, theta, alpha, num_iterations, cost=True):
    """
        Perform gradient descent given a data set with an arbitrary
        number of features.
        Returns cost function history if specified.
    """

    m = len(values)
    cost_history = []

    for i in range(num_iterations):
        theta -= alpha * np.dot((np.dot(features, theta) - values), features) / m
        cost = compute_cost(features, values, theta)
        cost_history.append(cost)

    if cost == False:
        return theta

    return theta, pd.Series(cost_history)

def compute_r_squared(data, predictions):
    """ Compute and return the coefficient of determination for the data. """

    mean = data.mean()
    r_squared = 1 - np.square(data - predictions).sum() / np.square(data - mean).sum()

    return r_squared

#----------------------
