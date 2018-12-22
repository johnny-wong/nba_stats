"""
Created on Fri Nov 16 15:42:31 2018

@author: Johnny Wong
"""
import datetime as dt
import requests
import pandas as pd
import numpy as np
import time

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
        self.REQUEST_HEADERS = {
            'user-agent': self.USER_AGENT,
        }
        print('NBAStats class created')

    def get_games(self):
        ''' Returns the dataframe containing info on the games '''
        return self.df_games

    def get_boxscores(self, game_id):
        ''' Returns the dictionary containing each game's boxscore '''
        return self.game_boxscores

    def get_player_stats(self):
        ''' Returns dictionary of player's stats '''
        return self.player_stats

    def get_player_name_id_dict(self):
        ''' Dictionary mapping player's name to their id '''
        return self.player_name_id

    def update_stats(self, date, season_type='Regular Season', seconds_wait=5):
        ''' 
        For all finished games on provided date, retrieve stats and update 
        game boxscores and player stats 
        '''
        if not isinstance(date, dt.date):
            raise TypeError("date supplied must be of type datetime.date")

        elif season_type not in ['Regular Season', 'Playoffs', 'Pre Season']:
            raise ValueError('season_type must be: Regular Season, Playoffs, or Pre Season')

        print('\nUpdating stats for {}'.format(date))
        # Constants    
        # Determine which NBA season
        if date.month >= 10:
            season_start_year = date.year
        else:
            season_start_year = date.year - 1
            
        season = str(season_start_year) + '-' + str(season_start_year + 1)[-2:]

        # Get df containing info from all finished games
        df_day_games = self._get_game_info(date, season, season_type, 
            self.REQUEST_HEADERS)
        self.df_games = self.df_games.append(df_day_games).drop_duplicates()

        # Update boxscores and all player stats
        for idx, game in df_day_games.iterrows():
            self._update_boxscore(date, game, season, season_type)

        print('Updated stats for {}\n'.format(date))

    def _get_game_info(self, date, season, season_type, 
        REQUEST_HEADERS, seconds_wait=5):
        '''
        Given a date, return a df containing info on finished games of that day
        '''
        # Constants used in parsing
        NBA_ID = '00'
        NBA_URL = 'https://stats.nba.com/stats/teamgamelogs'
        date_from = date
        date_to = date_from
        date_from_string = date_from.strftime('%m/%d/%Y')
        date_to_string = date_from_string

        nba_params = {
            'LeagueID': NBA_ID,
            'Season': season,
            'SeasonType': season_type,
            'DateFrom': date_from_string, 
            'DateTo': date_to_string,
            'Outcome': '' # Can set to 'W' or 'L' to just get winners or losers
        }

        print('Accessing stats.nba.com for games on {}'.format(date), end='.....')
        time.sleep(seconds_wait)
        r = requests.get(NBA_URL, params=nba_params, headers=REQUEST_HEADERS, 
            allow_redirects=False, timeout=15)
        assert r.status_code == 200
        print('Successful')

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

        if len(df_games) == 0:
            print('No games on {}'.format(date))
        return df_games

    def _parse_boxscore(self, date, GameID, matchup, season, season_type, 
        REQUEST_HEADERS, seconds_wait=5):
        ''' 
        Takes in the GameID in string format and returns a dataframe of the 
        boxscore, broken down by player.
        If game is not yet finished, will return a boxscore with NULL values
        >>> df_boxscore = parse_boxscore('0021800151')
        '''
        if not isinstance(GameID, str):
            raise TypeError('GameID must be string')
        
        URL_GAME_BOXSCORE = 'https://stats.nba.com/stats/boxscoretraditionalv2'
        boxscore_params = {
            'GameID': GameID,
            'Season': season,
            'SeasonType': season_type,
            'EndPeriod': '10',
            'EndRange': '28800',
            'RangeType': '0',
            'StartPeriod': '1',
            'StartRange': '0'
        }

        print('\nAccessing game {} ({} on {}) to get boxscore'.format(
            GameID, matchup, date), end='.....')
        time.sleep(seconds_wait)
        r_boxscore = requests.get(URL_GAME_BOXSCORE, params=boxscore_params, 
                                  headers=REQUEST_HEADERS, allow_redirects=False, timeout=15)

        assert r_boxscore.status_code == 200
        print('Successful')

        json_boxscore = r_boxscore.json()
        
        # 0 is player stats, 1 is team stats, 2 is starter bench stats
        player_stats = json_boxscore['resultSets'][0] 
        
        boxscore_headers = player_stats['headers'] 
        boxscore_stats = player_stats['rowSet']

        df_boxscore = pd.DataFrame(columns=boxscore_headers, 
            data=boxscore_stats)

        return df_boxscore

    def _update_player(self, date, player, home_team, home_team_id, 
        away_team, away_team_id,):
        '''
        Given a pd.Series, player, and other info about the game, update the 
        player's stats
        '''
        player_id = player['PLAYER_ID']
        player_name = player['PLAYER_NAME']
        print('Updating stats for {}'.format(player_name), 
            end='.' * (35 - len(player_name)))

        # Only update if not already existing data on that date
        try:
            if date in self.player_stats[player_id].index:
                update_player = False
                print('already updated')
            else:
                update_player = True
        except:
            update_player = True

        if update_player:
            # Update name to id dict
            if player_name not in self.player_name_id.keys():
                self.player_name_id[player_name] = player_id

            # Record whether it's home or away team
            if player['TEAM_ID'] == home_team_id:
                home_away = 'HOME'
                opp_team = away_team
                opp_team_id = away_team_id
            else:
                home_away = 'AWAY'
                opp_team = home_team
                opp_team_id = home_team_id

            # Convert to df to make it easier to add new columns later
            df_player_stats = player.to_frame().T
            
            # Add extra columns
            df_player_stats['Date'] = date
            df_player_stats['HOME_AWAY'] = home_away
            df_player_stats['OPP_TEAM_ABBREVIATION'] = opp_team
            df_player_stats['OPP_TEAM_ID'] = opp_team_id
            df_player_stats = df_player_stats.set_index('Date')

            try:
                self.player_stats[player_id] = self.player_stats[player_id].append(
                    df_player_stats)
                print('updated')
            except:
                # player didn't exist yet
                self.player_stats[player_id] = df_player_stats
                print('created')

    def _update_boxscore(self, date, game, season, season_type):
        ''' 
        Given a pd.Series, game, that contains info about a specific game,
        parse the boxscore from stats.nba.com and updates boxscore. Calls function
        to update player stats
        '''
        game_id = game['GAME_ID']
        if game_id not in self.game_boxscores.keys():
            # Assign home and away team
            home_away = game['HOME_AWAY']
            if home_away == 'HOME':
                home_team = game['TEAM_ABBREVIATION']
                home_team_id = game['TEAM_ID']
                away_team = game['OPP_TEAM_ABBREVIATION']
                away_team_id = game['OPP_TEAM_ID']
            else:
                home_team = game['OPP_TEAM_ABBREVIATION']
                home_team_id = game['OPP_TEAM_ID']
                away_team = game['TEAM_ABBREVIATION']
                away_team_id = game['TEAM_ID']

            boxscore = self._parse_boxscore(
                date,
                game_id,
                game['MATCHUP'],
                season, 
                season_type,
                self.REQUEST_HEADERS
                )

            self.game_boxscores[game_id] = boxscore

            # Update player stats
            for idx, player in boxscore.iterrows():
                # player_id = player['PLAYER_ID']
                self._update_player(date, player, home_team, home_team_id,
                    away_team, away_team_id)
        else:
            print('Game {} ({} on {}) is already recorded, no need to update'.format(
                game_id, game['MATCHUP'], date))

if __name__ == "__main__":
    test = NBAStats()
    test.update_stats(dt.date(2018, 9, 14))