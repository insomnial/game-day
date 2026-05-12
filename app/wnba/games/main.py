import requests
from datetime import datetime
from pytz import timezone
from requests import get


###############################################################################
#region Load variables
###############################################################################
# environment
ENDPOINT = 'https://site.api.espn.com/apis/site/v2/sports/basketball/wnba/scoreboard'


###############################################################################
#region Private functions
###############################################################################
def _get_json_blob() -> dict:
    response_json = get(
        url=ENDPOINT,
        headers={'Accept': 'application/json'}
    )
    return response_json.json()


###############################################################################
#region Public functions
###############################################################################
# Takes the entire blob and returns a cleaned dict of ranking
def get_games() -> dict:
    json_blob = _get_json_blob()
    events = json_blob['events']

    # strip down to what we want
    game_list = {}

    for game in events:
        # Process each game as needed
        event_datetime = datetime.strptime(game['date'], '%Y-%m-%dT%H:%MZ')
        utc_tz = timezone('UTC')
        event_datetime = utc_tz.localize(event_datetime)
        event_timestamp = int(event_datetime.timestamp())

        game_list[game['id']] = {
            'name': game['date'],
            'timestamp': event_timestamp,
            'status': game['status']
        }

    return game_list


# Main for testing, functions will be called by send_message.py
def main():
    response_json = requests.get(
        url=ENDPOINT,
        headers={'Accept': 'application/json'}
    )

    print(get_games())

# I forget this every effing time
if __name__ == '__main__':
    main()
