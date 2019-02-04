from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import datetime as dt
import re
import player_market_class

def get_links(date, chrome_path, url):
    '''
    Goes through ladbroke's NBA games page and returns a list of links to all open markets.
    '''
    driver = webdriver.Chrome(chrome_path)
    driver.get(url)

    boxes = driver.find_elements_by_class_name("fullbox")
    
    # Filter out promotional markets
    games = [box for box in boxes if 'BASKETBALL USA' in box.text]
    links = []

    for game in games:
        # filter out games not in today
        table = game.find_element_by_tag_name('table')
        if (date not in table.text) or ('Phone Betting Only' in table.text):
            # Not today or today but started
            continue

        try:
            link = game.find_element_by_tag_name("a")
            link_str = link.get_attribute('href')
            
            if re.search(r'nba/\d+-(.*)-v-(.*)/$', link_str):
                # Sometimes the game is shown but there is no valid link to the bets
                links.append(link_str)

        except:
            None
    driver.close()
    return links

def get_player_markets(link, chrome_path):
    '''
    Returns a list of strings parsed from ladbrokes player markets from input link
    '''
    driver = webdriver.Chrome(chrome_path)
    driver.get(link)

    # markets = driver.find_elements_by_class_name('additional-market-description')
    markets = driver.find_elements_by_class_name('additional-market')
    markets_of_interest = [
        'Total Points',
        'Total Rebounds',
        'Total Assists'
    ]

    main_markets = [market for market in markets if re.search(
        r'Total (Points|Rebounds|Assists)$', market.text)]

    # Scroll to top so that the first box isn't hidden by ladbrokes's ribbon
    driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
    time.sleep(1) # Wait for page to finish scrolling

    # Click on all markets of interest so that their odds appear and record what the odds are
    market_list = []
    prev_market_text = ''# There seems to be triples of every market for some reason
    for market in main_markets:
        market.click()
        time.sleep(0.5)
        market_text = market.text

        if market_text == prev_market_text:
            # Checks if 
            continue
        else:
            market_list.append(market_text)
            prev_market_text = market_text # To compare with next string

    driver.close()
    return market_list

def get_game_tuples(game_date=dt.date.today(),
                chrome_path=r"C:\Users\johnn\chromedriver\chromedriver.exe",
                url = "https://www.ladbrokes.com.au/sports/basketball/69460051-basketball-usa-nba/"):
    '''
    For supplied date, return a list of tuples each containing:
    - Game date (Sydney)
    - datetime when it was recorded
    - home team
    - away team
    - list of odds strings
    '''

    date_str = game_date.strftime("%d/%m/%Y")

    links = get_links(date_str, chrome_path, url)
    print('Got game links from LB\n')
    game_tuples = []
    for i, link in enumerate(links):
        # Find teams and record time
        teams = re.search(r'nba/\d+-(.*)-v-(.*)/$', link)
        home_team = teams.group(1)
        away_team = teams.group(2)

        odds_str_list = get_player_markets(link, chrome_path)
        
        game_tuple = (game_date, dt.datetime.now(), home_team, 
            away_team, odds_str_list)

        game_tuples.append(game_tuple)
        
        print('Got odds strings from {} ({}/{})'.format(link,
            i+1, len(links)))

    return game_tuples

def tuples_to_markets(list_tuples):
    '''
    Convert tuples of (datetime, home team, away team, list of odds string)
    into a list of PlayerMarkets
    '''
    player_markets_LB = []
    for game_tuple in list_tuples:
        game_date, date, home_team, away_team, odds_str_list = game_tuple
        for odds_str in odds_str_list:
            try:
                player_markets_LB.append(
                    player_market_class.PlayerMarketLadbrokes(game_date, date,
                        home_team, away_team, odds_str))
            except:
                print('Ladbrokes NOT ADDED: {}'.format(odds_str))
                continue

    return player_markets_LB
