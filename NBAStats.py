"""
Created on Fri Nov 16 15:42:31 2018

@author: Johnny Wong
"""
import datetime as dt
import requests
import pandas as pd
import numpy as np

class NBAStats():
    def __init__(
        self, 
        USER_AGENT=('Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
              'AppleWebKit/537.36 (KHTML, like Gecko) ' +
              'Chrome/70.0.3538.77 Safari/537.36'),
        ):
        self.player_stats = {}
        self.player_name_id = {}
        self.df_games = pd.DataFrame()
        self.game_boxscores = {}
        self.USER_AGENT = USER_AGENT

    def get_games(self):
        ''' Returns the dataframe containing info on the games '''
        return self.df_games

    def update_stats(self, date, season_type='Regular Season'):
        ''' 
        For all finished games on provided date, retrieve stats and update 
        game boxscores and player stats 
        '''
        if not isinstance(date, dt.date):
            raise TypeError("date supplied must be of type datetime.date")

        elif season_type not in ['Regular Season', 'Playoffs', 'Pre Season']:
            raise ValueError('season_type must be: Regular Season, Playoffs, or Pre Season')
        
        # Get df containing info from all finished games
        df_day_games = self._get_game_info(date, season_type)

        self.df_games = self.df_games.append(df_day_games) #TODO figure out how to append without creating duplicates
        print('Updated stats for {}'.format(date))

    def _get_game_info(self, date, season_type):
        '''
        Given a date, return a df containing info on finished games of that day
        '''
        # Constants used in parsing
        NBA_ID = '00'
        NBA_URL = 'https://stats.nba.com/stats/teamgamelogs'
        REQUEST_HEADERS = {
            'user-agent': self.USER_AGENT,
        }
        date_from = date
        date_to = date_from

        date_from_string = date_from.strftime('%m/%d/%Y')
        date_to_string = date_from_string

        # Determine which NBA season
        if date_from.month >= 10:
            season_start_year = date_from.year
        else:
            season_start_year = date_from.year - 1
            
        season = str(season_start_year) + '-' + str(season_start_year + 1)[-2:]

        nba_params = {
            'LeagueID': NBA_ID,
            'Season': season,
            'SeasonType': season_type,
            'DateFrom': date_from_string, 
            'DateTo': date_to_string,
            'Outcome': '' # Can set to 'W' or 'L' to just get winners or losers
        }

        r = requests.get(NBA_URL, params=nba_params, headers=REQUEST_HEADERS, 
            allow_redirects=False, timeout=15)
        assert r.status_code == 200
        
        json_dict = r.json() # Turns the json text into a python dict
        games_dict = json_dict['resultSets'][0] # Only has one element
        headers = games_dict['headers']
        
        GAME_ID_COL = headers.index('GAME_ID')
        DATE_COL = headers.index('GAME_DATE')
        MATCHUP_COL = headers.index('MATCHUP')
        games_list = games_dict['rowSet'] # List of list
        
        df_games = pd.DataFrame(columns=headers, data=games_list)
        df_games = df_games[['SEASON_YEAR', 'TEAM_ID', 'TEAM_ABBREVIATION',
                             'GAME_ID', 'GAME_DATE', 'MATCHUP', 'WL',
                             'PTS']]
        df_games['HOME_AWAY'] = df_games['MATCHUP'].apply(lambda x: 'HOME' if  'vs.' in x else 'AWAY')
        
        # Get the opponent's info
        df_games['TEAM_ABBREVIATION_OPP'] = df_games['MATCHUP'].apply(lambda x: x[-3:])
        df_games = pd.merge(df_games, df_games[['TEAM_ID', 'TEAM_ABBREVIATION', 'PTS']], 
                            left_on='TEAM_ABBREVIATION_OPP', right_on = 'TEAM_ABBREVIATION',
                            suffixes=('', '_OPP'))
        df_games = df_games.rename(columns={'TEAM_ABBREVIATION_OPP': 'OPP_TEAM_ABBREVIATION',
                                 'PTS_OPP': 'OPP_PTS',
                                 'TEAM_ID_OPP': 'OPP_TEAM_ID'
                                })
        
        # Remove duplicate column of 'OPP_TEAM_ABBREVIATION'
        df_games = df_games.loc[:,~df_games.columns.duplicated()]

        return df_games

test = NBAStats()
test.update_stats(dt.date(2018, 11, 14))
print(test.get_games())