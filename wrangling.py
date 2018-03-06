import pandas as pd
import pandasql

def num_rainy_days(filename):
    '''
        This function runs a SQL query on a dataframe of
        weather data. It returns one column and
        one row - a count of the number of days in the dataframe
        where the rain column is equal to 1.
    '''

    weather_data = pd.read_csv(filename)

    q = """
        SELECT COUNT(*) as num_rainy_days
        FROM weather_data
        WHERE CAST(rain AS integer) = 1
        """

    # Execute query against the pandas dataframe
    rainy_days = pandasql.sqldf(q.lower(), locals())

    return rainy_days

def max_temp_aggregate_by_fog(filename):
    '''
        This function runs a SQL query on a dataframe of
        weather data. It returns two columns and
        two rows - whether it was foggy or not (0 or 1) and
        the max temperature for that fog value.
    '''

    weather_data = pd.read_csv(filename)

    q = """
        SELECT fog, MAX(maxtempi) AS max_temp
        FROM weather_data
        GROUP BY fog
        """

    foggy_days = pandasql.sqldf(q.lower(), locals())
    return foggy_days
