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
env_path = Path(__file__).resolve().parent / '.env'
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
def formatPayload(conference: str,standings: dict) -> dict:
    output = {}
    if DEBUG:
        output['channel'] = f'{slack_channel_test}'
    else:
        output['channel'] = f'{slack_channel_prod}'

    blocks = []
    blocks.append({'type': 'context','elements': [{'type': 'plain_text','text': f'WNBA {conference} Standings','emoji': True}]})
    
    # # prints strings with inconsistent tabs as spaces
    # for team in standings.values():
    #     followed_teams = ['Valkyries']
    #     starred = ''
    #     if team['name'] in followed_teams:
    #         starred = ':star:'
    #     blockDict = {}
    #     blockDict['type'] = 'section'
    #     fields = []
    #     fields.append({
    #         'type': 'mrkdwn',
    #         'text': f'{int(team['rank'])}\t{team['name']}\t({team['overall']})\t{starred}'
    #     })
    #     blockDict['fields'] = fields
    #     blocks.append(blockDict)

    # print as a table with consistent spacing but cell borders
    blockDict = {'type':'table','column_settings':[{'align':'center'},{'align':'left'},{'align':'right'},{'align':'right'}]}
    rowsList=[[{'type':'rich_text','elements':[{'type':'rich_text_section','elements':[{'type':'text','text':'Rank'}]}]},{
        'type':'rich_text','elements':[{'type':'rich_text_section','elements':[{'type':'text','text':'Team'}]}]},{'type':
        'rich_text','elements':[{'type':'rich_text_section','elements':[{'type':'text','text':'Record'}]}]},{'type':
        'rich_text','elements':[{'type':'rich_text_section','elements':[{'type':'text','text':'Last 10'}]}]}]] # rows are a list of lists
    for team in standings.values():
        row = [] # create a new row which is a list of dicts for each team
        followed_teams = ['Golden State Valkyries']
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
                    'text': f'{team['rank']}'
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
                    'text': f'{team['overall']}'
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
                    'text': f'({team['stats']['Last Ten Games']})'
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
    print(f'Standings length: {len(standings)}') # logging
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
    for conference, standing in standings.items():
        payload = formatPayload(conference = conference, standings=standing)
        print(f'Standings for {conference} sending') # logging

        token = os.getenv('SLACK_BOT_TOKEN')
        url = 'https://slack.com/api/chat.postMessage'
        headers = {'Authorization': f'Bearer {token}', 'Content-type': 'application/json; charset=utf-8'}
        try:
            req = requests.post(url=url, headers=headers, data=json.dumps(payload)).json()
            print(f'Response {req['ok']}')
        except Exception as ex:
            print(ex)


if __name__ == '__main__':
    main()
