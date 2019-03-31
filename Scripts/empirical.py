import sys
import os
import pickle
import NBAStats
import numpy as np
import datetime as dt
import pandas as pd

parent_dir = os.path.dirname(os.getcwd())
# stats_file = os.path.join(parent_dir, 'Data', 'nba_stats.pickle')
stats_file = r'C:\Users\johnn\Desktop\github\nba_stats\Data\nba_stats.pickle'
print(stats_file)
nba_stats = pickle.load(open(stats_file, 'rb'))


def get_player_df(nba_stats, player, player_id=False):
    ''' Get the dataframe containing info on referenced player. If player_id=True, player id given instead of name'''
    if player_id:
        if player not in nba_stats.get_player_stats().keys():
            raise ValueError('player_id {} not found'.format(player))
        
        return nba_stats.get_player_stats()[player].sort_index(ascending=False)
    else:
        if player not in nba_stats.get_player_name_id_dict().keys():
            raise ValueError('player name {} not found'.format(player))
        
        return nba_stats.get_player_stats()[nba_stats.get_player_name_id_dict()[player]].sort_index(ascending=False)

def player_df_convert_numeric(player_df):
    ''' Returns a dataframe that converts relevant columns to numeric 
    Columns converted:
    MIN
    '''
    player_df['MIN'] = player_df['MIN'].apply(
        lambda str_min: int(str_min[:-3]) + int(str_min[-2:])/60.0 if str_min is not None else 0 )

    return player_df

def empirical_odds(player_name, stat, baseline, past_n_games):
    '''
    Returns a tuple of the theoretical odds from recent empirical data.
    theo_over_odds, theo_under_odds
    '''
    player_df = get_player_df(nba_stats, player_name)
    player_df = player_df_convert_numeric(player_df)
    player_df_played = player_df[player_df.MIN > 0]
    player_df_recent = player_df_played.head(past_n_games)

    assert player_df_recent.duplicated().sum() == 0

    ############## PLOT 100 EMPIRICAL
    n_overs = (player_df_recent[stat] > baseline).sum()
    n = len(player_df_recent)

    pr_over_baseline = n_overs/float(n)

    return 1/pr_over_baseline, 1/(1-pr_over_baseline)