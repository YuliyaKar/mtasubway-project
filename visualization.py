import matplotlib.pyplot as plt
import seaborn as sns

def entries_by_hour(data):
    """
        Plot a bar plot showing mean number of hourly entries as
        a function of hour.
    """

    fig = plt.figure()
    sns.barplot(x='HOUR', y='ENTRIESn_hourly', palette='Blues_d', data=data)
    plt.xlabel('Hour')
    plt.ylabel('Mean number of entries')
    plt.title('Hourly Number of Entries')

    plt.show()

    return fig

def unit_entries_rain(data):
    """
        Plot a bar plot showing mean number of entries for each turnstile unit
        indicating rainy (or not) weather.
    """

    fig = plt.figure()
    sns.barplot(x='UNIT', y='ENTRIESn_hourly', hue='rain', data=data)
    plt.xlabel('Turnstile Unit')
    plt.ylabel('Mean number of entries')
    plt.title('Entries at Units')

    plt.show()

    return fig
