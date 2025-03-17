from crawlpage import GetDate, GetToday, prettyPrint
import requests, json, os, datetime


DEBUG = 0
MARCH_MADNESS = 0

##
## Builds each section-block by adding each game. Formats the time from UTC
##  timestamp and puts it into Slack-variable regex to display per users'
##  set timezone.
## Ex
##   05:00 PM
##       Berkeley
##       Stanford
def formatPayload(gamesDict : dict) -> dict:
    output = {}
    if DEBUG:
        output['channel'] = os.getenv('SLACK_CHANNEL_TEST')
    else:
        output['channel'] = os.getenv('SLACK_CHANNEL_PROD')

    blocks = []
    blocks.append({"type": "context","elements": [{"type": "plain_text","text": "All times local.","emoji": True}]})
    if MARCH_MADNESS: 
        # march madness header
        blocks.append({"type": "section","text": {"type": "mrkdwn","text": ":party-porg: :party-slug: :partyotter: *March Madness* :partyotter: :party-slug: :party-porg:\n[ <https://www.ncaa.com/brackets/basketball-women/d1/2025|Bracket> ]"}})
    blockDict = {}
    blockDict['type'] = 'section'
    fields = []
    for gameKey in gamesDict.keys():
        fields.append({
            'type': 'mrkdwn',
            # "<!date^1392734382^{time}|Posted 2014-02-18 6:39:42 AM PST>"
            'text': f'*<!date^{gamesDict[gameKey][2]}^' + '{time}' + f'|{gamesDict[gameKey][2]}>*\n\t{gamesDict[gameKey][0]}\n\t{gamesDict[gameKey][1]}\n'
            })
    blockDict['fields'] = fields
    blocks.append(blockDict)
    output['blocks'] = blocks
    return output


##
## Splits the list of games into chunks that are allowed to fit into Slack block
##  sections (currently set at limit of 10). Adds in reverse using pop() method.
##
# TODO: We don't need to do this, each section can only hold 10 items but each 
#       message can hold many sections. Remove this and break apart the list of
#       games in the payload prep section instead.
def chunkDict(inputDict : dict) -> dict:
    MAX_SIZE = 8 # limit is 10 parts per section
    outputList = []
    dictPieces = len(inputDict.keys()) // MAX_SIZE

    for i in range(dictPieces): # build chunk of games for this section, starting from the end
        subDict = {}
        for j in range(MAX_SIZE):
            item = inputDict.popitem()
            subDict[item[0]] = item[1]
        outputList.append(subDict)
    # any remaining partial chunk needs to be added in reverse as well
    subDict = {}
    for i in range(len(inputDict.keys())):
        item = inputDict.popitem()
        subDict[item[0]] = item[1]
    outputList.append(subDict) # add remaining chunk into output

    return outputList


##
## Collect games and send a message to Slack
##
def main():
    if DEBUG :
        gamesDict = GetDate(datetime.datetime.strptime('2025/03/19', '%Y/%m/%d'))
    else :
        gamesDict = GetToday()
    prettyPrint(gamesDict) # just for logging I guess?
    if len(gamesDict.keys()) == 0:
        print("No games today")
        return

    token = os.getenv('SLACK_BOT_TOKEN')

    url = 'https://slack.com/api/chat.postMessage'
    headers = {'Authorization': f'Bearer {token}', 'Content-type': 'application/json; charset=utf-8'}
    # split dictionary
    for chunk in chunkDict(gamesDict):
        payload = json.dumps(formatPayload(chunk))

        try:
            req = requests.post(url=url, headers=headers, data=payload)
            print(json.loads(req.content))
        except Exception as ex:
            print(ex)


if __name__ == '__main__':
    main()
