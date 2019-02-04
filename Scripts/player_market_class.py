import re

class PlayerMarket():
    def __init__(self, time_rec, home_team, away_team,
        overs_exchange, unders_exchange, 
        player, stat, baseline, odds_over, odds_under):

        player_name_dict = {
            'Al Farouq Aminu':'Al-Farouq Aminu',
            'Willie Cauley Stein':'Willie Cauley-Stein',
            'Wendell Carter':'Wendell Carter Jr.',
            'D.J Augustin':'D.J. Augustin',
            'Karl Anthony Towns':'Karl-Anthony Towns',
            'T.J Warren':'T.J. Warren',
            'Darius MIller':'Darius Miller',
            'Marvin Bagley': 'Marvin Bagley III',
            'P.J. Tucker':'PJ Tucker',
            'J.J. Redick':'JJ Redick',
            'Otto Porter': 'Otto Porter Jr.',
            'C.J. McCollum': 'CJ McCollum',
            'Deandre Bembry': 'Deandre\' Bembry',
            }

        if player in player_name_dict:
            self.player = player_name_dict[player]
        else:
            self.player = player
            
        self.time_rec = time_rec
        self.home_team = home_team
        self.away_team = away_team
        self.overs_exchange = overs_exchange
        self.unders_exchange = unders_exchange
        self.stat = stat
        self.baseline = baseline
        self.odds_over = odds_over
        self.odds_under = odds_under

    def get_market_name(self):
        '''
        Returns an identifier for the market, doesn't include odds e.g.
        Joe Ingles - 5.5 AST
        '''
        return '{} - {} {}'.format(self.player, self.baseline, self.stat)

    def calc_spread(self):
        '''
        Returns the excess probability over 100% implied by the market's odds.
        Negative means there is an arb opportunity
        '''
        return 1/float(self.odds_over) + 1/float(self.odds_under) - 1

    def combine_odds(self, player_market):
        '''
        Takes in another PlayerMarket and returns a PlayerMarket with the
        best combined odds of both.
        '''
        if not isinstance(player_market, PlayerMarket):
            raise TypeError(('player_market must be of class PlayerMarket. '
                'It is currently a {}').format(type(player_market)))

        elif self.get_market_name() != player_market.get_market_name():
            raise ValueError(('Not the same markets\n'
                'This market: {}\nplayer_market: {}').format(
                self.get_market_name(), player_market.get_market_name()))

        exchange1_overs = self.odds_over
        exchange2_overs = player_market.odds_over

        if exchange2_overs > exchange1_overs:
            best_odds_overs = exchange2_overs
            exchange_overs = player_market.overs_exchange
        else:
            best_odds_overs = exchange1_overs
            exchange_overs = self.overs_exchange

        exchange1_unders = self.odds_under
        exchange2_unders = player_market.odds_under

        if exchange2_unders > exchange1_unders:
            best_odds_unders = exchange2_unders
            exchange_unders = player_market.unders_exchange
        else:
            best_odds_unders = exchange1_unders
            exchange_unders = self.unders_exchange

        time_rec = min(self.time_rec, player_market.time_rec)

        market_best_odds = PlayerMarket(time_rec, 
            self.home_team, self.away_team, 
            exchange_overs, exchange_unders,
            self.player, self.stat, self.baseline, 
            best_odds_overs, best_odds_unders)

        return market_best_odds 

    def __repr__(self):
        string_repr = ('{} @ {} - {:%d-%b %H:%M}\n'
            '{}\nOvers {:5} {}\nUnders {:5} {}').format(
            self.away_team, self.home_team, self.time_rec,
            self.get_market_name(),
            self.odds_over, self.overs_exchange,
            self.odds_under, self.unders_exchange
            )
        return string_repr

    def __string__(self):
        return self.__repr__()

class PlayerMarketSportsBet(PlayerMarket):
    def __init__(self, time_rec, home_team, away_team, odds_str):
        '''
        Parses the string output scraped from sportsbet website and creates a PlayerMarket instance
        String of format:
        'Kemba Walker - Points\nKemba Walker Over (+23.5)\nKemba Walker Under (+23.5)\n1.90\n1.83'
        '''

        # Converts all stat headings to format I have in NBA_Stats
        stat_dict = {
            'Points':'PTS',
            'Rebounds':'REB',
            'Assists':'AST'
            }
        
        re_name = r'(.+) - '
        name = re.match(re_name, odds_str).group(1)
        name = re.sub(r' Jr(\s|$)', ' Jr.', name) # Replace Jr with Jr.

        re_stat = r' - (.+)\n'
        stat = re.search(re_stat, odds_str).group(1)
        stat_NBA = stat_dict[stat]

        re_baseline = r'\+(\d+\.5)'
        baseline = re.search(re_baseline, odds_str).group(1)
        baseline_num = float(baseline)

        re_odds_over = r'^(\d\.\d{2})$'
        odds_over = re.search(re_odds_over, odds_str, re.M).group(1)
        odds_over_num = float(odds_over)
        
        re_odds_under = r'(\d\.\d{2})$'
        odds_under = re.search(re_odds_under, odds_str).group(1)
        odds_under_num = float(odds_under)
        
        PlayerMarket.__init__(self, time_rec, home_team, away_team,
                            'sportsbet', 'sportsbet',
                            name, stat_NBA,
                            baseline_num, odds_over_num, 
                            odds_under_num)
        
        return None

class PlayerMarketLadbrokes(PlayerMarket):
    def __init__(self, time_rec, home_team, away_team, odds_str):
        '''
        Parses the string output scraped from sportsbet website and creates a PlayerMarket instance
        String of format:
        'Reggie Jackson Total Assists\nOver (4.5)\n1.87\nUnder (4.5)\n1.87'
        '''

        # Converts all stat headings to format I have in NBA_Stats
        stat_dict = {
            'Points':'PTS',
            'Rebounds':'REB',
            'Assists':'AST'
            }
        
        # Name
        re_name = r'^(.*) Total '
        name = re.search(re_name, odds_str).group(1)
        
        name = re.sub(r' Jr(\s|$)', ' Jr.', name) # Replace Jr with Jr.

        # Stat
        re_stat = r' Total (.+)\n'
        stat = re.search(re_stat, odds_str).group(1)
        stat_NBA = stat_dict[stat]

        # Baseline
        re_baseline = r'Over \((\d+\.5)\)'
        baseline = re.search(re_baseline, odds_str).group(1)
        baseline_num = float(baseline)

        # Odds over
        re_odds_over = r'\n(\d+.*)\n'
        odds_over = re.search(re_odds_over, odds_str).group(1)
        odds_over_num = float(odds_over)
        
        # Odds under
        re_odds_under = r'\n(\d+.*)$'
        odds_under = re.search(re_odds_under, odds_str).group(1)
        odds_under_num = float(odds_under)
        
        PlayerMarket.__init__(self, time_rec, home_team, away_team,
                            'ladbrokes', 'ladbrokes', 
                            name, stat_NBA,
                            baseline_num, odds_over_num, 
                            odds_under_num)
        return None