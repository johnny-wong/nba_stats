import NBAStats
import pickle
import os
import datetime as dt
import time

###################################
START_DATE = dt.date(2018, 12, 28)
END_DATE = dt.date(2019, 1, 1)

AUTO_SAVE_RATE = 3 # Number of days before autosave
SECONDS_WAIT = 3 # Seconds to wait before sending request
###################################


parent_dir = os.path.dirname(os.getcwd())
file_directory = os.path.join(parent_dir, 'Data', 'nba_stats.pickle')

# print(os.path.dirname)
if START_DATE > END_DATE:
    raise ValueError('START_DATE {} must be before END_DATE {}'.format(
        START_DATE, END_DATE))

if os.path.isfile(file_directory):
    print('Existing file found, creating backup and updating')
    nba_stats = pickle.load(open(file_directory, 'rb'))
    backup_dir = os.path.dirname(file_directory) + '\\backup\\nba_stats_backup.pickle'
    pickle.dump(nba_stats, open(backup_dir, 'wb'))

else:
    print('File not found, creating new nba_stats.pickle file')
    nba_stats = NBAStats.NBAStats()

update_date = END_DATE
count = 0

# Loop from END to START date so most recent games updated first.
while update_date >= START_DATE:
    # Autosave
    if count % AUTO_SAVE_RATE == 0 and count != 0:
        print('Autosaving', end='.....')
        pickle.dump(nba_stats, open(file_directory, 'wb'))
        nba_stats = pickle.load(open(file_directory, 'rb'))
        print('complete')

    # iterate through all dates
    nba_stats.update_stats(update_date, season_type='Regular Season', 
        seconds_wait=SECONDS_WAIT)
    update_date -= dt.timedelta(1)
    count += 1


pickle.dump(nba_stats, open(file_directory, 'wb'))
print('Updated stats from {} to {} and new file saved in {}'.format(
    START_DATE, END_DATE, file_directory))