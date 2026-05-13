import os, statsapi
from dotenv import load_dotenv
from pathlib import Path

from requests import get


###############################################################################
#region Load variables
###############################################################################
# environment
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)


###############################################################################
#region Private functions
###############################################################################


###############################################################################
#region Public functions
###############################################################################
def get_current_game_data(team_id) -> dict:
    # giants team_id = 137
    # mets team_id = 121
    # get team data
    response_json = get(url=f'https://statsapi.mlb.com/api/v1/teams/137', 
                        headers = {"content-type":"application/json"}).json()
    pass
    try:
        event_today = statsapi.schedule(team=team_id, sportId=1, include_series_status=True, date='05/12/2026')
        event_today = event_today[0]
        game_status = event_today['status']
        if game_status == 'In Progress':
            print(event_today['summary'])
            print(statsapi.linescore(event_today['game_id']))
        elif game_status == 'Scheduled':
            print(event_today['summary'])
            print(statsapi.linescore(event_today['game_id']))
    except Exception as e:
        print("No remaining games for today.")
        pass


# Main for testing, functions will be called by send_message.py
def main():

    get_current_game_data('137')
    get_current_game_data('121')


# I forget this every effing time
if __name__ == '__main__':
    main()
