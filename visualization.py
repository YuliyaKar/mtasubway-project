import matplotlib.pyplot as plt
import seaborn as sns

def entries_by_hour(data):
    """
        Plot bar plot showing mean number of hourly entries as
        a function of hour.
    """

    fig = plt.figure()
    sns.barplot(x='HOUR', y='ENTRIESn_hourly', palette='Blues_d', data=data)
    plt.xlabel('Hour')
    plt.ylabel('Mean number of entries')
    plt.title('Hourly Number of Entries')

    plt.show()

    return fig
