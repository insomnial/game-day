import requests, json, os, argparse
from dotenv import load_dotenv
from pathlib import Path
from time import sleep

from main import get_division_standings


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
    standings = standings[next(iter(standings))]
    blocks.append({"type": "context","elements": [{"type": "plain_text","text": f'{standings['div_name']}',"emoji": True}]})
    
    teams = standings['teams']
    for team in teams:
        rank_num = team['div_rank']
        rank_team = team['name']
        rank_wins = team['w']
        rank_losses = team['l']
        rank_gb = team['gb']
        rank_elim_num = team['elim_num']
        followed_teams = ['San Francisco Giants', 'New York Mets']
        starred = ''
        if rank_team in followed_teams:
            starred = ':star:'
        blockDict = {}
        blockDict["type"] = "section"
        fields = []
        fields.append({
            "type": "mrkdwn",
            "text": f'{rank_num}\t{rank_team} ({rank_wins}-{rank_losses})\t{starred}'
            # "text": f'{rank_num}\t{rank_team}\t{rank_wins}-{rank_losses}\tGB: {rank_gb}\tElim Num: {rank_elim_num}'
            })
        blockDict["fields"] = fields
        blocks.append(blockDict)
    output["blocks"] = blocks
    return output


###############################################################################
#region main
###############################################################################
def main():
    # populate with divisions we care about (League, Region)
    division_list = [
        (104, 204), # NL East
        (104, 203)  # NL West
    ]

    for division in division_list:
        standings = get_division_standings(division[0], division[1]) # (league, division)
        print(standings) # logging

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
