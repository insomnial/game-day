import requests, json, os, datetime, os
from dotenv import load_dotenv
from pathlib import Path

###############################################################################
#region Load variables
###############################################################################
# environment
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("API_KEY")
# request
base_url = 'https://api.sportradar.com/mlb/trial/v8'
locale = 'en'
year = '2026' #convert to use date time
season_type = 'REG'
format = 'json'


###############################################################################
#region Private functions
###############################################################################
def _request_full_standings() -> dict:
    #build request url for standings
    url = f'{base_url}/{locale}/seasons/{year}/{season_type}/standings.{format}'
    
    #build request headers
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key
    }

    try:
        req = requests.get(url=url, headers=headers)
        return json.loads(req.content)
    except Exception as ex:
        print(ex)
        return {}

# Helper function to pull out the division searched for
def _get_division_from_standings(standings : dict, leagueName : str, divisionName : str) -> dict:
    for league in standings['league']['season']['leagues']:
        if league['name'] == leagueName:
            for division in league['divisions']:
                if division['name'] == divisionName:
                    return division['teams']
    return {}


###############################################################################
#region Public functions
###############################################################################

# Gets the standings for the current day.
def get_division_standings(leagueName : str, divisionName : str) -> dict:
    fullStandings = _request_full_standings()
    # right now I only want the NL West #goGaints
    nlWestTeams = _get_division_from_standings(fullStandings, leagueName, divisionName)

    rankDict = {}
    for team in nlWestTeams:
        name = team['name']
        win = team['win']
        loss = team['loss']
        streak = team['streak']
        rank = int(team['rank']['division'])
        rankDict[rank] = f'{name} ({win}-{loss}, {streak})'
    return rankDict

# Main for testing, functions will be called by send_message.py
def main():
    standings = get_division_standings('National League', 'West')
    print(standings)
    standings = get_division_standings('National League', 'East')
    print(standings)

# I forget this every effing time
if __name__ == '__main__':
    main()
