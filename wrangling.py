import pandas as pd
import pandasql
import csv

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
    df['ENTRIESn_hourly'].fillna(1, inplace=True)

    return df
