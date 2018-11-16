import NBAStats
import pickle
import os

cwd = os.getcwd()
file_directory = cwd + '\\nba_stats.pickle'

nba_stats = pickle.load(open(file_directory, 'rb'))

print(nba_stats.get_games())
