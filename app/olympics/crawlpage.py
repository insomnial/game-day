from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import time
from datetime import datetime, timezone, timedelta, tzinfo
import json

# URL from NCAA website for women's basketball
BASE_URL = 'https://www.olympics.com/wmr-owg2026/schedules/api/ENG/schedule/lite/day'


##
## Convert a string time to UTC timestamp. Expects ET.
##
def formatStringToTimestampUtc(pulldate : datetime, timestring : str) -> str:
    timestring = timestring.replace('ET', '-0500') # expects ET string time
    newDateString = pulldate.strftime('%Y/%m/%d') + ' ' + timestring
    newDateTime = datetime.strptime(newDateString, '%Y/%m/%d %I:%M%p %z')
    return str(int(newDateTime.timestamp()))


##
## Load the URL, parse the DOM, and build a dictionary of the groups scheduled
##  for the day passed in.
##
def _loadDOM(pulldate : datetime, url : str) -> dict:
    request = Request(url)
    request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
    request.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
    with urlopen(request) as response:
        data = json.loads(response.read().decode())    
    return data['groups'] # groups contains the events

##
## Prints the parsed dictionary into a readable format.
##
def prettyPrint(gameDict : dict):
    print(json.dumps(gameDict, indent=2))

    
##
## Builds the URL to parse from the passed-in date and loads the URL into a DOM
##  object that we can parse.
##
def GetDate(pulldate : datetime) -> dict:
    dateString = pulldate.strftime('%Y-%m-%d')
    buildUrl = [BASE_URL]
    buildUrl.append(dateString)
    fullUrl = '/'.join(buildUrl)
    return _loadDOM(pulldate, fullUrl)


##
## Wrapper when date to return is the current date.
##
def GetToday() -> dict:
    searchDate = datetime.today()# + timedelta(days = 1)
    return GetDate(searchDate)


def main():
    prettyPrint(GetToday())
    # prettyPrint(GetDate(datetime.strptime('2024/12/15', '%Y/%m/%d')))
    a = True

if __name__ == '__main__':
    main()