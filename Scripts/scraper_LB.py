from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import datetime as dt
import re

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
            links.append(link.get_attribute('href'))
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

def get_all_odds_str(date=dt.date.today().strftime("%d/%m/%Y"),
                chrome_path=r"C:\Users\johnn\chromedriver\chromedriver.exe",
                url = "https://www.ladbrokes.com.au/sports/basketball/69460051-basketball-usa-nba/"):
    '''
    For supplied date, return a list containing all strings of player markets
    parsed from Ladbrokes
    '''

    links = get_links(date, chrome_path, url)
    odds_str = []
    for link in links:
        odds_str.extend(get_player_markets(link, chrome_path))

    return odds_str