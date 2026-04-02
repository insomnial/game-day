import requests, json, os, datetime, os
from dotenv import load_dotenv
from pathlib import Path

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
DEBUG = False


###############################################################################
#region Internal functions
###############################################################################
##
## Builds each section-block by adding each game. Formats the time from UTC
##  timestamp and puts it into Slack-variable regex to display per users'
##  set timezone.
## Ex
##   05:00 PM
##       Berkeley
##       Stanford
def formatPayload(title: str, standings: dict) -> dict:
    output = {}
    if DEBUG:
        output["channel"] = f"{slack_channel_test}"
    else:
        output["channel"] = f"{slack_channel_prod}"

    blocks = []
    blocks.append({"type": "context","elements": [{"type": "plain_text","text": title,"emoji": True}]})
    
    for rank in standings.keys():
        rank_num = rank
        rank_team = standings[rank]
        followed_teams = ['Giants', 'Mets']
        for team in followed_teams:
             if team in rank_team:
                 rank_team = f'{rank_team}\t:star:'
        blockDict = {}
        blockDict["type"] = "section"
        fields = []
        fields.append({
            "type": "mrkdwn",
            "text": f'{rank_num}\t{rank_team}'
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
        ('National League', 'East'),
        ('National League', 'West')
    ]

    for division in division_list:
        standings = get_division_standings(division[0], division[1]) # (League, Region)
        print(standings) # logging

        # format the payload for Slack
        payload = formatPayload(title = f'Standings for {division[0]} {division[1]}', standings=standings)
        print(payload) # logging

        token = os.getenv('SLACK_BOT_TOKEN')
        url = 'https://slack.com/api/chat.postMessage'
        headers = {'Authorization': f'Bearer {token}', 'Content-type': 'application/json; charset=utf-8'}
        try:
            req = requests.post(url=url, headers=headers, data=json.dumps(payload))
            print(json.loads(req.content))
        except Exception as ex:
            print(ex)


if __name__ == '__main__':
    main()
