import pandas as pd
import pandasql
import csv
import datetime

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

def avg_weekend_temperature(filename):
    '''
        This function runs a SQL query on a dataframe of
        weather data. The SQL query returns one column and
        one row - the average meantempi on days that are a Saturday
        or Sunday.
    '''

    weather_data = pd.read_csv(filename)

    q = """
        SELECT AVG(meantempi) as avg_temp
        FROM weather_data
        WHERE CAST(strftime('%w', date) AS integer) = 0 OR
                CAST(strftime('%w', date) AS integer) = 6
        """

    mean_temp_weekends = pandasql.sqldf(q.lower(), locals())
    return mean_temp_weekends


def fix_turnstile_data(filenames):
    '''
    Filenames is a list of MTA Subway turnstile text files. A link to an example
    MTA Subway turnstile text file can be seen at the URL below:
    http://web.mta.info/developers/data/nyct/turnstile/turnstile_110507.txt

    There are numerous data points included in each row of the
    a MTA Subway turnstile text file.

    This function updates each row in the text
    file so there is only one entry per row. A few examples below:
    A002,R051,02-00-00,05-28-11,00:00:00,REGULAR,003178521,001100739
    A002,R051,02-00-00,05-28-11,04:00:00,REGULAR,003178541,001100746
    A002,R051,02-00-00,05-28-11,08:00:00,REGULAR,003178559,001100775
    '''

    for name in filenames:

        f_in = open(name, 'r')
        f_out = open('updated_' + name, 'w')

        reader_in = csv.reader(f_in, delimiter=',')
        writer_out = csv.writer(f_out, delimiter=',')

        for line in reader_in:
            for i in range(3, len(line)-5, 5):
                writer_out.writerow(line[0:3] + line[i:i+5])

        f_in.close()
        f_out.close()

def create_master_turnstile_file(filenames, output_file):
    '''
        Takes the files in the list filenames, which all have the
        columns 'C/A, UNIT, SCP, DATEn, TIMEn, DESCn, ENTRIESn, EXISTn', and
        consolidates them into one file located at output_file.
    '''

    with open(output_file, 'w') as master_file:
        master_file.write('C/A,UNIT,SCP,DATEn,TIMEn,DESCn,ENTRIESn,EXITSn\n')

        for filename in filenames:
            f = open(filename, 'r')
            for line in f.readlines():
                master_file.write(line)

            f.close()

def filter_by_regular(filename):
    '''
        This function reads the csv file located at filename into a pandas
        dataframe and filter the dataframe to only rows where the 'DESCn'
        column has the value 'REGULAR'.
    '''

    turnstile_data = pd.read_csv(filename)
    turnstile_data = turnstile_data[turnstile_data.DESCn == 'REGULAR']

    return turnstile_data

def get_hourly_entries(df):
    '''
        The data in the MTA Subway Turnstile data reports on the cumulative
        number of entries and exits per row.
        This function changes cumulative entry numbers to a count of
        entries since the last reading. If there is any NaN, it is filled
        with 1.
    '''

    df['ENTRIESn_hourly'] = df['ENTRIESn'] - df['ENTRIESn'].shift(1)
    df['ENTRIESn_hourly'].fillna(0, inplace=True)

    # Remove rows where values < 0.0
    df = df[df['ENTRIESn_hourly'] >= 0.0]

    return df

def get_hourly_exits(df):
    '''
        The data in the MTA Subway Turnstile data reports on the cumulative
        number of entries and exits per row.
        This function changes cumulative exit numbers to a count of
        exits since the last reading. If there is any NaN, it is filled
        with 0.
    '''

    df['EXITSn_hourly'] = df['EXITSn'] - df['EXITSn'].shift(1)
    df['EXITSn_hourly'].fillna(0, inplace=True)

    return df

def time_to_hour(time):
    '''
        Given an input variable time that represents time in the format of:
        "00:00:00" (hour:minutes:seconds), this function extracts the hour part from the input variable time
        and returns it as an integer.
    '''
    hour = int(time[:2])

    return hour

def reformat_subway_dates(date):
    '''
        The dates in subway data are formattes in the format month-day-year.
        The dates in weather underground data are formatted year-month-day.

        This function takes as its input a date in the MTA Subway data format,
        and returns a date in the weather underground format.
    '''

    date_formatted = (datetime.datetime.strptime(date, '%m-%d-%y')).strftime(
                        '%Y-%m-%d')

    return date_formatted

def drop_null_columns(df):
    ''' This function drops the columns where all entries are null. '''

    cols = df.loc[:, df.isnull().all()].columns

    return df.drop(cols, axis=1)

def drop_one_value_columns(df):
    ''' This function drops the columns where all entries are identical. '''

    cols = [col for col in df.columns if len(df[col].unique()) == 1]

    return df.drop(cols, axis=1)

def drop_wrong_entries_exits_rows(df):
    '''
        There exist meaningless values in 'ENTRIESn' and 'EXITSn' columns:
        zeros or ones. Since in general these values must represent cumulative
        counts of entries/exits, it is unlikely to have such small numbers in
        this data set, comparing to the other values.
        This function drops such rows of a DataFrame df.
    '''
    df_clean = df[df["ENTRIESn"] > 1.]
    df_clean = df[df["EXITSn"] > 1.]

    return df_clean
