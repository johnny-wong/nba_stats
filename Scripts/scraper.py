# Import class
import player_market_class
import scraper_SB
import scraper_LB
import pandas as pd
import datetime as dt

def get_best_player_markets(market_date=dt.date.today()):
    '''
    Scrapes player markets from:
    - Ladbrokes
    - Sportsbet
    Returns a list of PlayerMarket with the best odds from any exchange
    '''
    # Convert dates to format required by scraper
    market_date_LB = market_date.strftime("%d/%m/%Y")
    market_date_SB = market_date.strftime("%d/%m/%y")

    # Get all odds strings from exchanges
    game_tuples_LB = scraper_LB.get_game_tuples(market_date_LB)
    print('Got all odds strings from LB\n')
    game_tuples_SB = scraper_SB.get_game_tuples(market_date_SB)
    print('Got all odds strings from SB\n')

    # Convert odds strings to PlayerMarkets
    player_markets_LB = []
    for game_tuple in game_tuples_LB:
        date, home_team, away_team, odds_str_list = game_tuple
        for odds_str in odds_str_list:
            try:
                player_markets_LB.append(
                    player_market_class.PlayerMarketLadbrokes(date,
                        home_team, away_team, odds_str))
            except:
                print('Ladbrokes NOT ADDED: {}'.format(odds_str))
                continue

    player_markets_SB = []
    for game_tuple in game_tuples_SB:
        date, home_team, away_team, odds_str_list = game_tuple
        for odds_str in odds_str_list:
            try:
                player_markets_SB.append(
                    player_market_class.PlayerMarketSportsBet(date,
                        home_team, away_team, odds_str))
            except:
                print('Sportsbet NOT ADDED: {}'.format(odds_str))
                continue

    best_markets = find_best_markets(player_markets_LB, player_markets_SB)
    print('Combined odds from all available exchanges to get best odds')
    return best_markets

def find_best_markets(*args):
    '''
    Takes in lists of PlayerMarket class items, combines common markets and 
    returns a list of unique markets with the best odds
    '''
    print('Finding best markets')
    if len(args) == 0:
        raise ValueError('No lists were given')

    # Combines all PlayerMarkets into one list
    master_list = []
    for arg in args:
        master_list += arg

    for player_market in master_list:
        if not isinstance(player_market, player_market_class.PlayerMarket):
            raise TypeError("Not all elements of input list are of PlayerMarket class")

    dict_master = {}

    for player_market in master_list:
        market_name = player_market.get_market_name()

        if market_name in dict_master:
            dict_master[market_name] = dict_master[market_name].combine_odds(player_market)
        else:
            dict_master[market_name] = player_market

    return list(dict_master.values())

