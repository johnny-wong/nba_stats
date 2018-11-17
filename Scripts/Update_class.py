import NBAStats
import pickle
import os
import datetime as dt

parent_dir = os.path.dirname(os.getcwd())
file_directory = os.path.join(parent_dir, 'Data', 'nba_stats.pickle')

START_DATE = dt.date(2018, 11, 4)
END_DATE = dt.date(2018, 11, 4)
print(os.path.dirname)
if START_DATE > END_DATE:
    raise ValueError('START_DATE {} must be before END_DATE {}'.format(START_DATE, END_DATE))

if os.path.isfile(file_directory):
    print('Existing file found, updating')
    nba_stats = pickle.load(open(file_directory, 'rb'))
else:
    print('File not found, creating new nba_stats.pickle file')
    nba_stats = NBAStats.NBAStats()

update_date = START_DATE
while update_date <= END_DATE:
    # iterate through all dates
    nba_stats.update_stats(update_date)
    update_date += dt.timedelta(1)
pickle.dump(nba_stats, open(file_directory, 'wb'))
print('New file saved in {}'.format(file_directory))