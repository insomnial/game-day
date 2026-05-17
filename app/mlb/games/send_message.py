import requests, json, os, argparse
from dotenv import load_dotenv
from pathlib import Path
from time import sleep

from pytz import timezone
from main import get_current_game_data
from datetime import datetime


###############################################################################
#region Load variables
###############################################################################
# environment
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)
api_key = os.getenv('API_KEY')
slack_token = os.getenv('SLACK_BOT_TOKEN')
slack_channel_test = os.getenv('SLACK_CHANNEL_TEST')
slack_channel_prod = os.getenv('SLACK_CHANNEL_PROD')

#region DEBUG
parser = argparse.ArgumentParser()
parser.add_argument('--live', action='store_true', help='Send to live channel')
args = parser.parse_args()

DEBUG = not args.live
GAME_DIR = 'stack_game/'

###############################################################################
#region Internal functions
###############################################################################
def formatPayload(game: dict) -> dict:
    output = {}
    blocks = []
    context_string = game['series_status'] if game['series_status'] != None else game['status']
    blocks.append({'type': 'context','elements': [{'type': 'plain_text','text': f'{context_string}','emoji': True}]})
    
    game_datetime = datetime.strptime(game['game_datetime'], '%Y-%m-%dT%H:%M:%SZ')
    utc_tz = timezone('UTC')
    game_datetime = utc_tz.localize(game_datetime)
    game_datetime_string = game_datetime.strftime('%Y-%m-%d %H:%M:%S')
    game_datetime_timestamp = int(game_datetime.timestamp())
    game_status = game['status']

    if DEBUG:
        output['channel'] = f'{slack_channel_test}'
        output['post_at'] = 1778991896
    else:
        output['channel'] = f'{slack_channel_prod}'
        output['post_at'] = game_datetime_timestamp - 3600 # an hour ahead of time

    if DEBUG or game_status == 'Pre-Game':
        # TODO create message with summary
        blockDict = {}
        blockDict['type'] = 'section'
        fields = []
        fields.append({
            'type': 'mrkdwn',
            'text': f'*{game['summary']}*\n<!date^{game_datetime_timestamp}^' + '{date_pretty} {time}' + f'^{'https://url'}|{game_datetime_string}>'
            # <!date^{timestamp value}^' + '{text format}' + f'^{extra data}|{fallback string}>
            # <!date^{timestamp value}^|{blob['timestamp']}>
            })
        blockDict['fields'] = fields
        blocks.append(blockDict)
        output['blocks'] = blocks
        return output

    else:
        # using stored message ID of initial summary post, delete existing message and post new message with linescore
        pass


###############################################################################
#region main
###############################################################################
def main():
    # populate with divisions we care about (League, Region)
    team_list = [
        137, # giants team_id = 137
        121  # mets team_id = 121
    ]

    for team_id in team_list:
        if DEBUG:
            game_blob = get_current_game_data(team_id, '05/16/2026') # (team_id)
            print(game_blob) # logging
        else:
            # gets current day if not specified
            game_blob = get_current_game_data(team_id) # (team_id)

        for game in game_blob:
            # debug
            if DEBUG: print(json.dumps(game, indent=4))

            # format the payload for Slack
            payload = formatPayload(game=game)
            print(payload) # logging

            token = os.getenv('SLACK_BOT_TOKEN')
            url = 'https://slack.com/api/chat.scheduleMessage'
            headers = {'Authorization': f'Bearer {token}', 'Content-type': 'application/json; charset=utf-8'}
            try:
                req_json = (requests.post(url=url, headers=headers, data=json.dumps(payload))).json()
            except Exception as ex:
                print(ex)
                exit(1)
            if req_json['ok']:
                scheduled_message_id = req_json['scheduled_message_id']
                cache_filename = f'mlb_{game['game_id']}'
                with open(f'{GAME_DIR}{cache_filename}.json', 'w') as f:
                    json.dump(req_json, f, indent=4)
            else:
                print(f"Error scheduling message for game {game['game_id']}: {req_json['error']}")
            print(req_json)


if __name__ == '__main__':
    main()
