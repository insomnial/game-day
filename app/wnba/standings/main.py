import os, requests, json
from dotenv import load_dotenv
from pathlib import Path


###############################################################################
#region Load variables
###############################################################################
# environment
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
ENDPOINT = 'https://site.api.espn.com/apis/v2/sports/basketball/wnba/standings'


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
        if stat['name'] in ['overall', 'Home', 'Road', 'vs. Div.', 'vs. Conf.', 'Last Ten Games']:
            stats[stat['name']] = stat['displayValue']
        else:
            stats[stat['name']] = stat['value']

    return stats

def _get_standings_conference(json_blob) -> dict:

    clean_standings = {}
    current_rank = 1
    for team in json_blob:
        stats = _populate_stats(team['stats'])
        team_name = team['team']['name']
        clean_standings[current_rank] = {
            'name': team_name, 
            'overall': stats['overall'], 
            'rank': current_rank
        }
        current_rank += 1

    return clean_standings


###############################################################################
#region Public functions
###############################################################################
# Takes the entire blob and returns a cleaned dict of ranking
def get_standings() -> dict:
    json_blob = _get_json_blob()
    conferences = json_blob['children']

    standings = {}

    for conference in conferences:
        conference_name = conference['name']
        conference_standings = _get_standings_conference(conference['standings']['entries'])
        print(f'{conference_name}\n{conference_standings}\n')
        standings[conference_name] = conference_standings

    return standings   


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
