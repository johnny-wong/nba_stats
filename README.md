# NBA Stats

Language: Python 3

## Motivation
1. Learn to scrape lots of data from the web. Got help from multiple youtube videos and one very helpful [blog post](http://practicallypredictable.com/2017/12/21/web-scraping-nba-team-matchups-box-scores/)
2. Explore the data, and try to think creatively about how I can apply my stats/modelling knowledge to find interesting relationships.
3. Compare my results with the market and see if there are any opportunities. In other words, compare my probabilities with available odds implied probabilities.
4. ???
5. Profit

## Progress
- Finished working version of NBA scraper. But will likely have to change when I think of something extra I want during my analysis
- Shown FGA is Poisson process
- Created notebook to check past 100 games of any player with a focus on determining the probability they score under/over some given baseline. Also runs statistical significance test for whether the average points per game is different for wins and losses.
- Streamlined above analysis into a tool that aids my betting. 
- Analysis on whether Christmas day has any significant effect on player stats
- Analysis on home court advantage w.r.t. player stats as well as team wins.
- Built web scraper for SportsBet
- Finish scraper for ladbrokes
- Built tool to automatically compare scraped markets to theo
- Create class to aggregate markets from different exchanges

## To do
- Minutes per game analysis MPG ~ opposing team, home/away, time since last game, performance last game
- Poisson model for FG3M
- Script to record market odds
- Backtester
- Add player's team, opponent's team, home/away, game date to PlayerMarket class
- Script to run multiple models over PlayerMarkets
