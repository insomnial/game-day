import requests, json, os, argparse
from dotenv import load_dotenv
from pathlib import Path
from time import sleep

from main import get_games
from hashlib import md5
from requests import post


###############################################################################
#region Load variables
###############################################################################
# environment
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
api_key = os.getenv('API_KEY')
slack_token = os.getenv('SLACK_BOT_TOKEN')
slack_channel_test = os.getenv('SLACK_CHANNEL_TEST')
slack_channel_prod = os.getenv('SLACK_CHANNEL_PROD')
CURRENT_HASH = ''
try:
    with open('hash.txt', 'r') as f:
        CURRENT_HASH = f.read()
except FileNotFoundError:
    CURRENT_HASH = ''

#region DEBUG
parser = argparse.ArgumentParser()
parser.add_argument('--live', action='store_true', help='Send to live channel')
args = parser.parse_args()

DEBUG = not args.live


###############################################################################
#region Internal functions
###############################################################################
def formatPayload(blob: dict) -> dict:
    output = {}
    # TODO: set this to the game time 
    output['post_at'] = blob['timestamp'] - 3600 # an hour ahead of time
    if DEBUG:
        output['channel'] = f'{slack_channel_test}'
        output['post_at'] = 1778568300
    else:
        output['channel'] = f'{slack_channel_prod}'

    blocks = []
    blocks.append({"type": "context","elements": [{"type": "plain_text","text": 'WNBA Game',"emoji": True}]})
    
    followed_teams = ['Valkyries']
    starred = ''
    for followed_team in followed_teams:
        if followed_team in blob['name']: starred = ':star:'
    blockDict = {}
    blockDict["type"] = "section"
    fields = []
    fields.append({
        "type": "mrkdwn",
        "text": f'*{blob['name']}*\n<!date^{blob['timestamp']}^' + '{date_pretty} {time}' + f'^{blob['links'][0]['href']}|{blob['timestamp']}>\t{starred}'
        # <!date^{gamesDict[gameKey][2]}^' + '{time}' + f'|{gamesDict[gameKey][2]}>
        # <!date^{blob['timestamp']}^|{blob['timestamp']}>
    })
    blockDict["fields"] = fields
    blocks.append(blockDict)
    output["blocks"] = blocks
    return output


###############################################################################
#region main
###############################################################################
def main():
    events = get_games()
    print(events) # logging
    # version = '1.0.0'
    # hash = md5(f'{str(events)}{version}'.encode()).hexdigest()
    # if hash == CURRENT_HASH:
    #     print('No changes detected, exiting.')
    #     return
    # else:
    #     print('Changes detected, sending message to Slack.')
    #     with open('hash.txt', 'w') as f:
    #         f.write(hash)

    for event in events.values():
        # format the payload for Slack
        payload = formatPayload(blob=event)
        #print(payload) # logging

        token = os.getenv('SLACK_BOT_TOKEN')
        url = 'https://slack.com/api/chat.scheduleMessage'
        # https://docs.slack.dev/reference/methods/chat.scheduleMessage/
        headers = {'Authorization': f'Bearer {token}', 'Content-type': 'application/json; charset=utf-8'}
        try:
            req = post(url=url, headers=headers, data=json.dumps(payload))
            print(req.json())
        except Exception as ex:
            print(ex)


if __name__ == '__main__':
    main()
