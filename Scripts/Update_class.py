import NBAStats
import pickle
import os
import datetime as dt
import time

###################################
START_DATE = dt.date(2016, 1, 1)
END_DATE = dt.date(2017, 1, 1)
###################################


parent_dir = os.path.dirname(os.getcwd())
file_directory = os.path.join(parent_dir, 'Data', 'nba_stats.pickle')


print(os.path.dirname)
if START_DATE > END_DATE:
    raise ValueError('START_DATE {} must be before END_DATE {}'.format(
        START_DATE, END_DATE))

if os.path.isfile(file_directory):
    print('Existing file found, updating')
    nba_stats = pickle.load(open(file_directory, 'rb'))
else:
    print('File not found, creating new nba_stats.pickle file')
    nba_stats = NBAStats.NBAStats()

update_date = START_DATE
count = 0
AUTO_SAVE_RATE = 15 # Number of days before autosave
while update_date <= END_DATE:
    # Autosave
    if count % AUTO_SAVE_RATE == 0 and count != 0:
        print('Autosaving', end='.....')
        pickle.dump(nba_stats, open(file_directory, 'wb'))
        nba_stats = pickle.load(open(file_directory, 'rb'))
        print('complete')

    # iterate through all dates
    nba_stats.update_stats(update_date, season_type='Regular Season', 
        seconds_wait=2)
    update_date += dt.timedelta(1)
    count += 1


pickle.dump(nba_stats, open(file_directory, 'wb'))
print('Updated stats from {} to {} and new file saved in {}'.format(
    START_DATE, END_DATE, file_directory))