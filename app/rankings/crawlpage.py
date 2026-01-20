import urllib.request
from bs4 import BeautifulSoup
import urllib
import time
from datetime import datetime, timezone, timedelta, tzinfo
from certifi import contents


# URL from NCAA website for women's basketball
BASE_URL = 'https://www.ncaa.com/rankings/basketball-women'
# filter options so we pull a reasonable amount of games
division = 'd1'
filter = 'associated-press' # ap rankings


##
## Load the URL, parse the DOM, and build a dictionary of the rankings.
## Returns the parsed rankings in a dictionary such that:
##   key: rank
##   value: (team, record)
##
def _loadDOM(url : str) -> dict:
    mysite = urllib.request.urlopen(url).read()
    soup_mysite = BeautifulSoup(mysite, features='html.parser')

    # find all the game divs
    rankings = {}
    for g in soup_mysite.find_all('article', {'class': 'rankings-content overflowable-table-region layout--content-left'}):
        contents = g.contents[1]
        contents = contents.contents[3]
        for row in contents:
            if len(rankings) < 10 and row != '\n':
                # row = row.contents[1]
                temp = row.contents[1]
                rank = temp.contents[0]
                temp = row.contents[3]
                school = temp.contents[0]
                temp = row.contents[5]
                record = temp.contents[0]
                rankings[rank] = (school, record)
    return rankings


##
## Get a rankings dictionary from the NCAA site.
##
def GetRankings() -> dict:
    buildUrl = [BASE_URL]
    buildUrl.append(division)
    buildUrl.append(filter)
    fullUrl = '/'.join(buildUrl)
    return _loadDOM(fullUrl)


##
## Prints the parsed dictionary into a readable format.
##
def prettyPrint(rankings : dict):
    outString = f"Rank School              Record" + "\n"
    outString = outString + "-"*40 + "\n"
    for rank in rankings.keys():
        outString = outString + f" {rank:>2}     {rankings[rank][0]:<20}    {rankings[rank][1]:>4}" + "\n"
    print(outString)


if __name__ == '__main__':
    prettyPrint(GetRankings())
