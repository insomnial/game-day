import requests, json, os, argparse
from dotenv import load_dotenv
from pathlib import Path
from time import sleep

from main import get_standings
from hashlib import md5


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
def formatPayload(standings: dict) -> dict:
    output = {}
    if DEBUG:
        output["channel"] = f"{slack_channel_test}"
    else:
        output["channel"] = f"{slack_channel_prod}"

    blocks = []
    blocks.append({"type": "context","elements": [{"type": "plain_text","text": 'NWSL Standings',"emoji": True}]})
    
    for team in standings.values():
        followed_teams = ['Bay FC', 'Angel City FC']
        starred = ''
        if team['name'] in followed_teams:
            starred = ':star:'
        blockDict = {}
        blockDict["type"] = "section"
        fields = []
        fields.append({
            "type": "mrkdwn",
            "text": f'{int(team['rank'])}\t{team['name']}\t{int(team['points'])}\t({team['overall']})\t{starred}'
        })
        blockDict["fields"] = fields
        blocks.append(blockDict)
    output["blocks"] = blocks
    return output


###############################################################################
#region main
###############################################################################
def main():
    standings = get_standings()
    print(standings) # logging
    version = '1.0.0'
    hash = md5(f'{str(standings)}{version}'.encode()).hexdigest()
    if hash == CURRENT_HASH:
        print('No changes detected, exiting.')
        return
    else:
        print('Changes detected, sending message to Slack.')
        with open('hash.txt', 'w') as f:
            f.write(hash)

    # format the payload for Slack
    payload = formatPayload(standings=standings)
    print(payload) # logging

    token = os.getenv('SLACK_BOT_TOKEN')
    url = 'https://slack.com/api/chat.postMessage'
    headers = {'Authorization': f'Bearer {token}', 'Content-type': 'application/json; charset=utf-8'}
    try:
        req = requests.post(url=url, headers=headers, data=json.dumps(payload))
    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    main()
