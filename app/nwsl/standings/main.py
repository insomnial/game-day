import os, requests, json
from dotenv import load_dotenv
from pathlib import Path


###############################################################################
#region Load variables
###############################################################################
# environment
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
ENDPOINT = 'https://site.api.espn.com/apis/v2/sports/soccer/usa.nwsl/standings'


###############################################################################
#region Private functions
###############################################################################
def _get_json_blob() -> dict:
    response_json = requests.get(
        url=ENDPOINT,
        headers={'Accept': 'application/json'}
    )
    return response_json.json()

def _populate_stats(json_blob) -> dict:
    stats = {}
    for stat in json_blob:
        if stat['name'] == 'overall':
            stats['overall'] = stat['displayValue']
        else:
            stats[stat['name']] = stat['value']

    return stats

###############################################################################
#region Public functions
###############################################################################
# Takes the entire blob and returns a cleaned dict of ranking
def get_standings() -> dict:
    json_blob = _get_json_blob()
    standings = json_blob['children'][0]['standings']['entries'] 

    clean_standings = {}
    for team in standings:
        stats = _populate_stats(team['stats'])
        team_name = team['team']['name']
        # print(f'{stats['rank']:2.0f}\t{team_name:18}\t{stats['points']:2.0f}') #logging
        # clean_standings[int(stats['rank'])] = {'name': team_name, 'overall': stats['overall'], 'points': stats['points']}
        clean_standings[int(stats['rank'])] = {
            'name': team_name, 
            'overall': stats['overall'], 
            'points': stats['points'],
            'rank': stats['rank']
        }

    return clean_standings

# Main for testing, functions will be called by send_message.py
def main():
    response_json = requests.get(
        url=ENDPOINT,
        headers={'Accept': 'application/json'}
    )
    print(json.dumps(response_json.json(), indent=4))

    print(get_standings())

# I forget this every effing time
if __name__ == '__main__':
    main()
