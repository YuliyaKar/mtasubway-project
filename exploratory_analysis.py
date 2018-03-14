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

def cut_outliers(data, filter_col, p):
    """
        Filter data from outliers points.

        Parameters
        ---------
        data: DataFrame to process.
        filter_col: column that contains outliers.
        p: fraction of data to cut.

        Return
        -------
        data_filtered: filtered DataFrame.
    """

    q1 = data[filter_col].quantile(p)
    q2 = data[filter_col].quantile(1 - p)

    data_filtered = data[data[filter_col] >= q1]
    data_filtered = data_filtered[data_filtered[filter_col] <= q2]

    return data_filtered

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

def plot_cost_history(alpha, cost_history):
    """ Plot the cost function history. """

    cost_df = pd.DataFrame({'Cost_History': cost_history,
                            'Iteration': range(len(cost_history))})

    plot = plt.figure()
    cost_df.plot(x='Iteration', y='Cost_History', label='alpha = ' + str(alpha))
    plt.legend()

    return plot

def predict(data):
    """
        Choose relevant features and use linear regression model to
        fit the data. Values of theta are computed iteratively using gradient
        descent.
    """

    # Select features
    features = data[['rain', 'precipi', 'HOUR', 'meantempi',
                     'EXITSn_hourly']]

    # Add UNIT to features using dummy variables
    dummy_units = pd.get_dummies(data['UNIT'], prefix='unit_')
    features = features.join(dummy_units)

    # Values
    values = data['ENTRIESn_hourly']
    m = len(values)

    features, mu, sigma = normalize_features(features)
    features['ones'] = np.ones(m) # Add a column of 1s (y intercept)

    # Convert features and values to numpy arrays
    features_array = np.array(features)
    values_array = np.array(values)

    # Set values for alpha, number of iterations
    alpha = 0.1
    num_iterations = 75

    # Initialize theta, perform gradient descent
    theta_gradient_descent = np.zeros(len(features.columns))
    theta_gradient_descent, cost_history = gradient_descent(features_array,
                                                            values_array,
                                                            theta_gradient_descent,
                                                            alpha,
                                                            num_iterations)

    # Predict
    predictions = np.dot(features_array, theta_gradient_descent)

    return predictions, cost_history

#----------------------
