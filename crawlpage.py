import urllib.request
from bs4 import BeautifulSoup
import urllib
import time
from datetime import datetime, timezone, timedelta, tzinfo

# URL from NCAA website for women's basketball
BASE_URL = 'https://www.ncaa.com/scoreboard/basketball-women'
# filter options so we pull a reasonable amount of games
division = 'd1'
# filter = 'top-25' # regular season
filter = 'all-conf' # march madness


##
## Convert a string time to UTC timestamp. Expects ET.
##
def formatStringToTimestampUtc(pulldate : datetime, timestring : str) -> str:
    timestring = timestring.replace('ET', '-0500') # expects ET string time
    newDateString = pulldate.strftime('%Y/%m/%d') + ' ' + timestring
    newDateTime = datetime.strptime(newDateString, '%Y/%m/%d %I:%M%p %z')
    return str(int(newDateTime.timestamp()))


##
## Load the URL, parse the DOM, and build a dictionary of the games scheduled
##  for the day passed in. Sort them in reverse-order of gametime (relying on 
##  game URL as a secondary sort) because we're going to use pop() later on.
## Returns the parsed games in a dictionary such that:
##   key: game URL
##   value: game details (team one, team two, game timestamp)
##
def _loadDOM(pulldate : datetime, url : str) -> dict:
    mysite = urllib.request.urlopen(url).read()
    soup_mysite = BeautifulSoup(mysite, features='html.parser')

    gameList = {}
    gameFound = 0
    gameLogged = 0
    # find all the game divs
    for g in soup_mysite.find_all('div', {'class': 'gamePod gamePod-type-game status-pre'}):
        gameFound = gameFound + 1
        contents = g.contents[1]
        gamelink = contents.attrs['href']
        gametime = contents.find('span', {'class': 'game-time'}).string
        formattedTime = formatStringToTimestampUtc(pulldate, gametime)
        
        # <ul class='gamePod-game-teams'>
        # collect the teams and merge them into one listing
        teamList = []
        for teamInfo in contents.find_all('ul', {'class': 'gamePod-game-teams'}):
            for singleTeam in teamInfo.find_all('li', {'class': ''}):
                # <span class='gamePod-game-team-rank'>13</span>
                teamRank = singleTeam.find('span', {'class': 'gamePod-game-team-rank'}).string
                teamRank = f'#{teamRank}' if teamRank != None else '' # add a '#' sign if the ranking string exists
                # <span class='gamePod-game-team-name'>Duke</span>
                teamName = singleTeam.find('span', {'class': 'gamePod-game-team-name'}).string
                teamList.append(f'{teamRank}{' ' if teamRank != '' else ''}{teamName}')
        
            # save the games with the game URL as the key
            gameList[gamelink] = (teamList[0], teamList[1], formattedTime)
            gameLogged = gameLogged + 1
    
    # sort by timestamp, output is array of tuples -- (game URL, (game details))
    # reverse because future formatting uses pop() and it pulls from the end
    sorted_items = sorted(gameList.items(), key=lambda kv: (kv[1][2], kv[0]), reverse=True)
    gameList = {}
    for item in sorted_items: gameList[item[0]] = item[1] # recombine array of tuples into dictionary -- key: game URL, value: (game details)
    return gameList


##
## Prints the parsed dictionary into a readable format.
##
def prettyPrint(gameDict : dict):
    outString = ''
    for gameKey in gameDict.keys():
        outString = outString + gameDict[gameKey][2] + "\n"
        outString = outString + "\t" + gameDict[gameKey][0] + "\n" + "\t" + gameDict[gameKey][1] + "\n\n"
    print(outString)


##
## Builds the URL to parse from the passed-in date and loads the URL into a DOM
##  object that we can parse.
##
def GetDate(pulldate : datetime) -> dict:
    dateString = pulldate.strftime('%Y/%m/%d')
    buildUrl = [BASE_URL]
    buildUrl.append(division)
    buildUrl.append(dateString)
    buildUrl.append(filter)
    fullUrl = '/'.join(buildUrl)
    return _loadDOM(pulldate, fullUrl)


##
## Wrapper when date to return is the current date.
##
def GetToday() -> dict:
    searchDate = datetime.today()
    return GetDate(searchDate)


def main():
    # prettyPrint(GetToday())
    prettyPrint(GetDate(datetime.strptime('2024/12/15', '%Y/%m/%d')))
    a = True

if __name__ == '__main__':
    main()