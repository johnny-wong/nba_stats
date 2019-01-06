import re

class PlayerMarket():
    def __init__(self, exchange, player, stat, baseline, odds_over, odds_under):
        self.exchange = exchange
        self.player = player
        self.stat = stat
        self.baseline = baseline
        self.odds_over = odds_over
        self.odds_under = odds_under
    
    def get_exchange(self):
        return self.exchange
    
    def get_player(self):
        return self.player
    
    def get_stat(self):
        return self.stat
    
    def get_baseline(self):
        return self.baseline
    
    def get_odds_over(self):
        return self.odds_over
    
    def get_odds_under(self):
        return self.odds_under

    def __repr__(self):
        string_repr = '{} - {}\nOver {:^5}Under {:^4}\n{:^10}{:^10}'.format(
            self.get_player(), self.get_stat(),
            self.get_baseline(), self.get_baseline(),
            self.get_odds_over(), self.get_odds_under())
        return string_repr

    def __string__(self):
        return self.__repr__()

class PlayerMarketSportsBet(PlayerMarket):
    def __init__(self, odds_str):
        '''
        Parses the string output scraped from sportsbet website and creates a PlayerMarket instance
        String of format:
        'Kemba Walker - Points\nKemba Walker Over (+23.5)\nKemba Walker Under (+23.5)\n1.90\n1.83'
        '''

        # Converts all names to format I have in NBA_Stats
        player_name_dict = {
            'Al Farouq Aminu':'Al-Farouq Aminu',
            'Willie Cauley Stein':'Willie Cauley-Stein'
            }

        # Converts all stat headings to format I have in NBA_Stats
        stat_dict = {
            'Points':'PTS',
            'Rebounds':'REB',
            'Assists':'AST'
            }
        
        re_name = r'(.+) - '
        name = re.match(re_name, odds_str).group(1)
        name = re.sub(r' Jr(\s|$)', ' Jr.', name) # Replace Jr with Jr.
        if name in player_name_dict.keys():
            player = player_name_dict[name]
        else:
            player = name

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
        
        PlayerMarket.__init__(self, 'sportsbet', 
                             player, stat_NBA,
                             baseline_num, odds_over_num, 
                              odds_under_num)
        
        return None