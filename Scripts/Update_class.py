import NBAStats
import pickle
import os
import datetime as dt

cwd = os.getcwd()
file_directory = cwd + '\\nba_stats.pickle'

START_DATE = dt.date(2018, 11, 1)
END_DATE = dt.date(2018, 11, 15)

if os.path.isfile(file_directory):
    nba_stats = pickle.load(open(file_directory, 'rb'))
else:
    nba_stats = NBAStats.NBAStats()

if START_DATE > END_DATE:
    raise ValueError('START_DATE {} must be before END_DATE {}'.format(START_DATE, END_DATE))

update_date = START_DATE
while update_date <= END_DATE:
    # iterate through all dates
    nba_stats.update_stats(update_date)
    update_date += dt.timedelta(1)
pickle.dump(nba_stats, open(file_directory, 'wb'))

