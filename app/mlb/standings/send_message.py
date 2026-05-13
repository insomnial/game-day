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
    
    # print as a table with consistent spacing but cell borders
    col1 = 'Division'
    col2 = 'Team'
    col3 = 'Record'
    col4 = 'League'
    blockDict = {'type':'table','column_settings':[{'align':'center'},{'align':'left'},{'align':'right'},{'align':'center'}]}
    rowsList=[[{'type':'rich_text','elements':[{'type':'rich_text_section','elements':[{'type':'text','text':f'{col1}'}]}]},{
        'type':'rich_text','elements':[{'type':'rich_text_section','elements':[{'type':'text','text':f'{col2}'}]}]},{'type':
        'rich_text','elements':[{'type':'rich_text_section','elements':[{'type':'text','text':f'{col3}'}]}]},{'type':
        'rich_text','elements':[{'type':'rich_text_section','elements':[{'type':'text','text':f'{col4}'}]}]}]] # rows are a list of lists
    for team in standings['teams']:
        row = [] # create a new row which is a list of dicts for each team
        followed_teams = ['New York Mets', 'San Francisco Giants']
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
                    'text': f'{team['div_rank']}'
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
                    'text': f'{team['w']} - {team['l']}'
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
                    'text': f'{team['league_rank']}'
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
            req = requests.post(url=url, headers=headers, data=json.dumps(payload)).json()
            print(f'Response successful {req['ok']}')
        except Exception as ex:
            print(ex)


if __name__ == '__main__':
    main()
