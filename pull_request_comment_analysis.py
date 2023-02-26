import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions
from query import pprint
from query import run_query
import scipy.stats as stats

# Pulls API Keys from keys.txt file
keys = open("keys.txt", "r")
api_key = keys.readline().rstrip('\n')
url = keys.readline().strip('\n')
keys.close()
if api_key == "apikey" or url == "url":
    print("ERROR: need to put api key in keys.txt file")

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

# Preforms a Point-Biserial Correlation test and prints the result
def correlation_test(prs):
    state = []
    sentiment = []
    for pr in prs:
        if pr.state == 'CLOSED':
            s = 0
        elif pr.state == 'MERGED':
            s = 1
        else:
            continue
        state.append(s)
        sentiment.append(pr.sentiment)
    point_biserial = stats.pointbiserialr(state, sentiment)
    pvalue = round(point_biserial.pvalue, 4)
    rvalue = round(point_biserial.statistic, 4)
    print("State and sentiment are", end=" ")
    if pvalue > 0.05:
        print("not", end=" ")
    print("statisiticaly significant: p-value of", pvalue, "and R-value of", rvalue)      

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

if pull_type == "issues":
    pprint(data)

if pull_type == "pullRequests":
    data = json.loads(data)
    print("Performing sentiment analysis...")
    pull_requests = list_of_pr(data)

    merged = 0
    merged_sum = 0
    closed = 0
    closed_sum = 0
    for pr in pull_requests:
        print(pr)
        if pr.state == "MERGED":
            merged_sum += pr.sentiment
            merged+=1
        elif pr.state == "CLOSED":
            closed_sum += pr.sentiment
            closed+=1
        else: 
            continue

    print()
    # Prints average PR sentiment
    if merged == 0:
        print('No merged PR')
    else:
        print('Average sentiment for merged PR:', merged_sum/merged)

    if closed == 0:
        print('No closed PR')
    else:
        print('Average sentiment for closed PR:', closed_sum/closed)

    print()
    # Preform a Point-Biserial Correlation test
    correlation_test(pull_requests)
