import string
import csv
import pandas as pd

def mapper(fin_path, fout_path):
    """
        This mapper reads csv file of Subway-MTA dataset and
        writes the dictionary to the output file, where the keys indicate
        the weather type and the values are the number of ENTRIESn_hourly.
    """

    # Util function that takes in variables indicating whether it is foggy
    # and/or rainy and returns a formatted key that you should output.
    def format_key(fog, rain):
        return '{}fog-{}rain'.format(
            '' if fog else 'no',
            '' if rain else 'no'
        )

    fin = open(fin_path, 'r')
    fout = open(fout_path, 'w')

    reader_in = csv.reader(fin, delimiter=",")
    writer_out = csv.writer(fout, delimiter=",")

    for line in reader_in:

        if line[1] == "UNIT":
            continue

        writer_out.writerow([format_key(float(line[14]), float(line[15]))] + [line[6]])

    fin.close()
    fout.close()

def reducer(fin_path, fout_path):
    """
        Given the output of the mapper, the reducer writes one
        row per weather type, along with the average value of
        ENTRIESn_hourly for that weather type.
        The input is assumed to be sorted by weather type.
    """

    fin = open(fin_path, 'r')
    fout = open(fout_path, 'w')

    reader_in = csv.reader(fin, delimiter=",")
    writer_out = csv.writer(fout, delimiter=",")

    riders = 0      # The number of total tiders for this key
    num_hours = 0   # The number of hours with this key
    old_key = None

    for line in reader_in:

        # Omit irregular lines
        #if len(line) != 2:
        #    continue

        this_key, count_hours = line[0], float(line[1])

        if old_key and old_key != this_key:

            writer_out.writerow([old_key] + [num_hours / riders])
            riders = 0
            num_hours = 0

        old_key = this_key
        num_hours += count_hours
        riders += 1.

    if old_key:
        writer_out.writerow([old_key] + [num_hours / riders])

    fin.close()
    fout.close()
