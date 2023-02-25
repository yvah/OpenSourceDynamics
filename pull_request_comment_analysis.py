import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions
from query import pprint
from query import run_query

# Pulls API Keys from keys.txt file
keys = open("keys.txt", "r")
api_key = keys.readline().rstrip('\n')
url = keys.readline().strip('\n')
keys.close()

# IBM NLU authentication
authenticator = IAMAuthenticator(api_key)
natural_language_understanding = NaturalLanguageUnderstandingV1(
    version='2022-04-07',
    authenticator=authenticator
)
natural_language_understanding.set_service_url(url)

# Defines pull requests as objects
class Pull_Request:
    # Constructor takes in a json node representing a pr
    def __init__(self, pr):
        self.state = pr['state']
        self.number_of_comments = pr['comments']['totalCount']
        
        # NEEDS TO CHANGE
        # Takes all comments and concatenates into single string -> not efficient
        comments = ''
        for comment in pr['comments']['edges']:
           comments += comment['node']['bodyText'] + ' '
        self.comments = comments
        
        # IBM NLP
        response = natural_language_understanding.analyze(
            text=self.comments,
            features=Features(sentiment=SentimentOptions())).get_result()
        self.sentiment = response['sentiment']['document']['score']
    
    # Defines a print method for pr
    def __str__(self):
        return "<state: " + self.state + "; comments: " + str(self.number_of_comments) + "; sentiment: " + str(self.sentiment) + ">"

# Takes a json file and parses it into a list of Pull_Request objects
def list_of_pr(data):
    pull_requests = []
    for pr in data:
        # NEED TO IMPLEMENT BETTER ERROR HANDLING
        # Right now has to deal with pr that throw:
        # ApiException: Error: not enough text for language id, Code: 422
        # This should not be a problem once data is cleaned/filtered
        try:
            pull_requests.append(Pull_Request(pr['node']))
        except Exception:
           pass
    return pull_requests

# Promts user for query
valid = True
print("Enter an access token: ", end="")
auth = input()
print("Enter a repo (owner/repo): ", end="")
temp = input()
owner_repo = temp.split("/")

pull_type = ""
if len(owner_repo) != 2:
    print("Invalid input")
    valid = False
else:
    print("Get issues or pull requests? (i or p): ", end="")
    letter = input()

    if letter == "i":
        pull_type = "issues"
    elif letter == "p":
        pull_type = "pullRequests"
    else:
        print("Invalid input")
        valid = False

if valid:
    data = run_query(auth, owner_repo[1], owner_repo[0], pull_type)

if (pull_type == "issues"):
    pprint(data)

if (pull_type == "pullRequests"):
    data = json.loads(data)
    print("Performing sentiment analysis...")
    pull_requests = list_of_pr(data)

    merged = 0
    merged_sum = 0
    closed = 0
    closed_sum = 0
    for pr in pull_requests:
        print(pr)
        if (pr.state == "MERGED"):
            merged_sum += pr.sentiment
            merged+=1
        elif (pr.state == "CLOSED"):
            closed_sum += pr.sentiment
            closed+=1
        else: 
            continue

    # Prints average PR sentiment
    if(merged == 0):
        print('No merged PR')
    else:
        print('Average sentiment for merged PR:', merged_sum/merged)

    if(closed == 0):
        print('No closed PR')
    else:
        print('Average sentiment for closed PR:', closed_sum/closed)
