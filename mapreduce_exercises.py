import string
import csv

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
