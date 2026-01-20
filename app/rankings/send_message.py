import requests, json, os, datetime

import crawlpage

# save these for later
DEBUG = 0
MARCH_MADNESS = 0

##
## Builds each section-block by adding each rank.
##
def formatPayload(rankings : dict) -> dict:
    output = {}
    if DEBUG:
        output['channel'] = os.getenv('SLACK_CHANNEL_TEST')
    else:
        output['channel'] = os.getenv('SLACK_CHANNEL_PROD')

    # create block array
    blocksDict = {}
    blocksDict['type'] = 'table'
    # if MARCH_MADNESS: 
    #     # march madness header
    #     blocks.append({"type": "section","text": {"type": "mrkdwn","text": ":party-porg: :party-slug: :partyotter: *March Madness* :partyotter: :party-slug: :party-porg:"}})
    #     blocks.append({"type": "section","text": {"type": "mrkdwn","text": "[ <https://www.ncaa.com/brackets/basketball-women/d1/2025|Bracket> ] [ <https://fantasy.espn.com/games/tournament-challenge-bracket-women-2025/group?id=69a29d96-97bf-43b8-91ed-de5a30560f15|Slacking Off WBB Challenge> ]"}})
    
    # build headers
    headerRows = [
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": "Rank",
                                "style": {
                                    "bold": True
                                }
                            }
                        ]
                    }
                ]
            },
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": "School",
                                "style": {
                                    "bold": True
                                }
                            }
                        ]
                    }
                ]
            },
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": "Record",
                                "style": {
                                    "bold": True
                                }
                            }
                        ]
                    }
                ]
            }
    ]
    allRows = []
    allRows.append(headerRows)

    # build rank rows
    dataRows = []
    for rank in rankings.keys():
        allRows.append([
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": f"{rank}"
                            }
                        ]
                    }
                ]
            },
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": f"{rankings[rank][0]}"
                            }
                        ]
                    }
                ]
            },
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": f"{rankings[rank][1]}"
                            }
                        ]
                    }
                ]
            }
        ])

    blocksDict['rows'] = allRows
		
    # attach rows of the table to the output block
    output['blocks'] = [blocksDict]

    return output

##
## Collect games and send a message to Slack
##
def main():
    rankings = crawlpage.GetRankings()

    crawlpage.prettyPrint(rankings) # just for logging I guess?

    token = os.getenv('SLACK_BOT_TOKEN')

    url = 'https://slack.com/api/chat.postMessage'
    headers = {'Authorization': f'Bearer {token}', 'Content-type': 'application/json; charset=utf-8'}
    payload = json.dumps(formatPayload(rankings))

    try:
        req = requests.post(url=url, headers=headers, data=payload)
        print(json.loads(req.content))
    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    DEBUG = 0
    MARCH_MADNESS = 0
    main()
