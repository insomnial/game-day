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
    
    # print as a table with consistent spacing but cell borders
    col1 = 'Rank'
    col2 = 'Team'
    col3 = 'Points'
    col4 = 'Record'
    blockDict = {'type':'table','column_settings':[{'align':'center'},{'align':'left'},{'align':'right'},{'align':'right'}]}
    rowsList=[[{'type':'rich_text','elements':[{'type':'rich_text_section','elements':[{'type':'text','text':f'{col1}'}]}]},{
        'type':'rich_text','elements':[{'type':'rich_text_section','elements':[{'type':'text','text':f'{col2}'}]}]},{'type':
        'rich_text','elements':[{'type':'rich_text_section','elements':[{'type':'text','text':f'{col3}'}]}]},{'type':
        'rich_text','elements':[{'type':'rich_text_section','elements':[{'type':'text','text':f'{col4}'}]}]}]] # rows are a list of lists
    for team in standings.values():
        row = [] # create a new row which is a list of dicts for each team
        followed_teams = ['Bay FC']
        starred = ''
        if team['name'] in followed_teams:
            team['name'] = f'-- {team['name']} --'

        # we need one dict for each column of rank, team name, record, and streak
        # COL rank
        rowDict = {} # list of dicts for this row
        rowDict['type'] = 'rich_text'
        rowDict['elements'] = [
            {
                'type': 'rich_text_section',
                'elements': [{
                    'type': 'text',
                    'text': f'{int(team['rank'])}'
                }]
            }
        ]
        row.append(rowDict)

        # COL team name
        rowDict = {} # list of dicts for this row
        rowDict['type'] = 'rich_text'
        rowDict['elements'] = [
            {
                'type': 'rich_text_section',
                'elements': [{
                    'type': 'text',
                    'text': f'{team['name']} {starred}'
                }]
            }
        ]
        row.append(rowDict)

        # COL record
        rowDict = {} # list of dicts for this row
        rowDict['type'] = 'rich_text'
        rowDict['elements'] = [
            {
                'type': 'rich_text_section',
                'elements': [{
                    'type': 'text',
                    'text': f'{int(team['points'])}'
                }]
            }
        ]
        row.append(rowDict)

        # COL streak
        rowDict = {} # list of dicts for this row
        rowDict['type'] = 'rich_text'
        rowDict['elements'] = [
            {
                'type': 'rich_text_section',
                'elements': [{
                    'type': 'text',
                    'text': f'({team['overall']})'
                }]
            }
        ]
        row.append(rowDict)

        rowsList.append(row)
    blockDict['rows'] = rowsList
    print(blockDict)

    blocks.append(blockDict)

    output['blocks'] = blocks

    return output


###############################################################################
#region main
###############################################################################
def main():
    standings = get_standings()
    print(standings) # logging
    version = '1.0.0'
    hash = md5(f'{str(standings)}{version}'.encode()).hexdigest()
    if not DEBUG and hash == CURRENT_HASH:
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
