# NBA Stats

Language: Python 3

## Motivation
1. Learn to scrape lots of data from the web. Got help from multiple youtube videos and one very helpful [blog post](http://practicallypredictable.com/2017/12/21/web-scraping-nba-team-matchups-box-scores/)
2. Explore the data, and try to think creatively about how I can apply my stats/modelling knowledge to find interesting relationships.
3. Compare my results with the market and see if there are any opportunities. In other words, compare my probabilities with available odds implied probabilities.

## Progress
- Finished working version of NBA scraper. But will likely have to change when I think of something extra I want during my analysis
- Shown FGA is Poisson process

## Files
NBAStats.py contains the class implementation of my web scraper.

nba_stats.pickle stores all the scraped data.

update_stats.py is a script that actually takes an instance of the class (the pickled file) and updates it.

Jupyter notebooks used for exploratory analysis.
