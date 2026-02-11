from crawlpage import GetDate, GetToday, prettyPrint
import requests, json, os, datetime, dateutil

DEBUG = 0

##
## Builds each section-block by adding each game. Formats the time from UTC
##  timestamp and puts it into Slack-variable regex to display per users'
##  set timezone.
## Ex
##   05:00 PM
##       Berkeley
##       Stanford
def formatPayload(groupDict : dict) -> dict:
    output = {}
    if DEBUG:
        output['channel'] = os.getenv('SLACK_CHANNEL_TEST')
    else:
        output['channel'] = os.getenv('SLACK_CHANNEL_OLYMPICS')

    blocks = []
    blocks.append({"type": "header","text": {"type": "plain_text","text": "Olympic Events Today", "emoji": True}})
    blocks.append({"type": "context","elements": [{"type": "plain_text","text": "All times local.","emoji": True}]})
    blockDict = {}
    blockDict['type'] = 'section'
    fields = []
    for eventTimestamp in groupDict.keys():
        event = groupDict[eventTimestamp]
        fields.append({
            'type': 'mrkdwn',
            # "<!date^1392734382^{date_short} {time}|Posted 2014-02-18 6:39:42 AM PST>"
            'text': f'*<!date^{int(eventTimestamp)}^' + '{date_short} {time}' + f'|{event["startDate"]}>*\n\t{event["title"]}\n\t{event["subTitle"]}\n\t{':first_place_medal:' if event["hasMedals"] == True else ''}\n'
            })
    blockDict['fields'] = fields
    blocks.append(blockDict)
    output['blocks'] = blocks
    return output


##
## Splits the list of games into chunks that are allowed to fit into Slack block
##  sections (currently set at limit of 10). Adds in reverse using pop() method.
##
def chunkDict(inputDict : dict) -> dict:
    MAX_SIZE = 8 # limit is 10 parts per section
    outputList = []
    dictPieces = len(inputDict) // MAX_SIZE

    for i in range(dictPieces): # build chunk of games for this section, starting from the end
        subDict = {}
        for j in range(MAX_SIZE):
            item = inputDict.popitem() # pop from the beginning of the sorted dictionary
            subDict[item[0]] = item[1]
        outputList.append(subDict)
    # any remaining partial chunk needs to be added in reverse as well
    subDict = {}
    for i in range(len(inputDict)):
            item = inputDict.popitem()
            subDict[item[0]] = item[1]
    outputList.append(subDict) # add remaining chunk into output

    return outputList


def _formatGroups(groupDict : dict) -> dict:
    now = datetime.datetime.now().timestamp()
    output = {}
    for group in groupDict:
        timestamp = (dateutil.parser.parse(group['startDate'])).timestamp()
        if timestamp > now: # only add future events
            output[timestamp] = group
    output = dict(sorted(output.items(), reverse=True)) # sort by timestamp
    return output

##
## Collect games and send a message to Slack
##
def main():
    groupsToday = GetToday()
    groupsToday = _formatGroups(groupsToday) # format the groups into a dictionary with timestamp keys for sorting
    prettyPrint(groupsToday) # just for logging I guess?
    if len(groupsToday) == 0:
        print("No groups today")
        return

    token = os.getenv('SLACK_BOT_TOKEN')

    url = 'https://slack.com/api/chat.postMessage'
    headers = {'Authorization': f'Bearer {token}', 'Content-type': 'application/json; charset=utf-8'}
    # split dictionary
    for chunk in chunkDict(groupsToday):
        payload = json.dumps(formatPayload(chunk))

        try:
            req = requests.post(url=url, headers=headers, data=payload)
            print(json.loads(req.content))
        except Exception as ex:
            print(ex)


if __name__ == '__main__':
    main()
