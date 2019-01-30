from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import datetime as dt
import re

def get_links(date, chrome_path, url):
    ''' 
    date in dd/mm/yy format
    Goes through sportsbet's NBA games page and returns a list of links to all open markets.
    '''

    driver = webdriver.Chrome(chrome_path)
    driver.get(url)

    games = driver.find_elements_by_class_name("linkMultiMarket_fcmecz0")
    
    # Filter for date's games that haven't started already
    today_games = [game for game in games if date in game.find_element_by_class_name('time_fbgyqei').text]
    
    links = [game.get_attribute('href') for game in today_games]
    driver.close()
    return links

def get_player_markets(link,
                        chrome_path=r"C:\Users\johnn\chromedriver\chromedriver.exe"):
    '''
    Returns a list of strings parsed from sportsbets player markets from input link
    '''
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(chrome_path, options=options)
    driver.get(link)

    markets = driver.find_elements_by_class_name("touchArea_fgteabt")

    markets_of_interest = ['Top Markets', # To minimise as default is opened
                           'Player Points Markets', 
                           'Player Rebounds Markets', 
                           'Player Assists Markets']
    main_markets = [market for market in markets if market.text in markets_of_interest]

    for market in main_markets:
        market.click()
        time.sleep(1)

    # Find player markets e.g. Donovan Mitchell - Points
    # Must be maximised windows for class name accordionItemDesktop_f1pa6f05
    player_markets = driver.find_elements_by_class_name("accordionItemDesktop_f1pa6f05")

    player_markets_of_interest = ['- Points', '- Rebounds', '- Assists']
    main_player_markets = [market for market in player_markets if any(
        stat in market.text for stat in player_markets_of_interest)]

    # Scroll to top so that the first box isn't hidden by Sportsbet's ribbon
    driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
    time.sleep(1) # Wait for page to finish scrolling

    # Open all the markets to see odds and record them
    market_list = []
    for player_market in main_player_markets:
        player_market.click()
        time.sleep(0.5)

        market_list.append(player_market.text)
    
    driver.close()
    
    return market_list

def get_game_tuples(date=dt.date.today().strftime("%d/%m/%y"),
                chrome_path=r"C:\Users\johnn\chromedriver\chromedriver.exe",
                url="https://www.sportsbet.com.au/betting/basketball-us/nba-matches"):
    '''
    For supplied date, return a list of tuples each containing:
    - datetime when it was recorded
    - home team
    - away team
    - list of odds strings
    '''

    links = get_links(date, chrome_path, url)
    print('Got game links from SB\n')
    game_tuples = []
    for i, link in enumerate(links):
        # Find teams and record time
        teams = re.search(r'nba-matches/(.*)-at-(.*)-\d+$', link)
        home_team = teams.group(2)
        away_team = teams.group(1)

        odds_str_list = get_player_markets(link, chrome_path)
        
        game_tuple = (dt.datetime.now(), home_team, 
            away_team, odds_str_list)

        game_tuples.append(game_tuple)
        
        print('Got odds strings from {} ({}/{})'.format(link,
            i+1, len(links)))

    return game_tuples