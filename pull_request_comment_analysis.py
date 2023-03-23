import json
from time import time
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions, EmotionOptions
from pprint import pprint
from query import run_query, write_to_file
import scipy.stats as stats

# Pulls API Keys from keys.txt file
keys = open('keys.txt', 'r')
api_key = keys.readline().rstrip('\n')
url = keys.readline().strip('\n')
keys.close()
if api_key == 'apikey' or url == 'url':
    print('ERROR: need to put api key in keys.txt file')

# IBM NLU authentication
authenticator = IAMAuthenticator(api_key)
natural_language_understanding = NaturalLanguageUnderstandingV1(
    version='2022-04-07',
    authenticator=authenticator
)
natural_language_understanding.set_service_url(url)


# Defines repositories as objects
class Repository:
    def __init__(self, data):
        # Creat list of PullRequest objects
        self.pull_requests = list_of_pr(data)

        # Calculate average sentiment for closed/merged prs
        merged = merged_sum = closed = closed_sum = 0
        for pr in self.pull_requests:
            if pr.state == 'MERGED':
                merged_sum += pr.sentiment
                merged += 1
            elif pr.state == 'CLOSED':
                closed_sum += pr.sentiment
                closed += 1
            else:
                continue
        self.merged_average = self.closed_average = None
        if merged != 0:
            self.merged_average = round(merged_sum / merged, 4)
        if closed != 0:
            self.closed_average = round(closed_sum / closed, 4)

        # Preform Point Biserial test
        self.p_value = self.r_value = None
        if self.merged_average is not None and self.closed_average is not None:
            point_biserial = correlation_test(self.pull_requests)
            self.p_value = round(point_biserial.pvalue, 4)
            self.r_value = round(point_biserial.statistic, 4)

    def __str__(self):
        result = ''
        # Print PullRequests
        for pr in self.pull_requests:
            result += str(pr) + '\n'
        result += '\n'

        # Print averages
        if self.merged_average is None:
            result += 'No merged PR\n'
        else:
            result += 'Average sentiment for merged PR: ' + str(self.merged_average) + '\n'
        if self.closed_average is None:
            result += 'No closed PR\n'
        else:
            result += 'Average sentiment for closed PR: ' + str(self.closed_average) + '\n'
        result += '\n'

        # Print correlation
        if self.p_value is None:
            result += 'Can not preform a correlation test\n'
        else:
            result += 'State and sentiment are '
            if self.p_value > 0.05:
                result += 'not '
            result += 'statistically significant: p-value of ' + str(self.p_value) + ' and R-value of ' + str(
                self.r_value)

        return result


# Defines pull requests as objects
class PullRequest:
    # Constructor takes in a json node representing a pr
    def __init__(self, pr):
        self.state = pr['state']
        self.number_of_comments = pr['commentCount']

        # NEEDS TO CHANGE
        # Takes all comments and concatenates into single string -> not efficient
        comments = ''
        for comment in pr['comments']:
            comments += comment['bodyText'] + ' '
        self.comments = comments

        # IBM NLP
        response = natural_language_understanding.analyze(
            text=self.comments,
            features=Features(sentiment=SentimentOptions(), emotion=EmotionOptions())).get_result()
        # print(response)
        self.sentiment = round(response['sentiment']['document']['score'], 4)
        # Creates an array to store emotion scores
        self.emotion = [['sadness', 0], ['joy', 0], ['fear', 0], ['disgust', 0], ['anger', 0]]
        for i in range(5):
            self.emotion[i][1] = round(response['emotion']['document']['emotion'][self.emotion[i][0]], 4)

        # print(self.emotion)
        # self.main_emotion = max(self.emotion)
        # self.s = ""
        # for i in range(5):
        #    self.s += self.emotion[i][0] + ": " + self.emotion[i][1] + "\n"

    # Defines a print method for pr
    def __str__(self):
        s = str(self.emotion)
        return "<state: " + self.state + "; comments: " + str(self.number_of_comments) + "; sentiment: " + str(
            self.sentiment) + ")>\n" + s


# Takes a json file and parses it into a list of PullRequest objectss
def list_of_pr(data):
    pull_requests = []
    for pr in data:
        # NEED TO IMPLEMENT BETTER ERROR HANDLING
        # ApiException: Error: not enough text for language id, Code: 422
        try:
            pull_requests.append(PullRequest(pr))
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
    return stats.pointbiserialr(state, sentiment)


# main function for testing code
if __name__ == '__main__':
    # '''
    # to test nlu
    file = open("fetched_data/flutter_PullRequests.json")
    data = json.load(file)
    print("Performing sentiment analysis...\n")
    start_time = time()
    repo = Repository(data)
    end_time = time()
    print(repo)
    print('\nSentiment analysis took', round(end_time - start_time, 3), 'seconds to run')

    '''
    # or with data extraction
    print("Enter an access token: ", end="")
    auth = input()
    
    pull_type = ""
    valid = False

    while not valid:
        print("Enter a repo (owner/repo): ", end="")
        owner_repo = input().split("/")
        if len(owner_repo) != 2:
            print("Invalid input")
        else:
            print("Get issues or pull requests? (i or p): ", end="")
            letter = input()

            if letter == "i":
                pull_type = "issues"
                valid = True
            elif letter == "p":
                pull_type = "pullRequests"
                valid = True
            else:
                print("Invalid input")

        if valid:
            data = run_query(auth, owner_repo[1], owner_repo[0], pull_type)

    if pull_type == "issues":
        pprint(data)

    if pull_type == "pullRequests":
        data = json.loads(data)
        print("Performing sentiment analysis...\n")
        start_time = time()
        repo = Repository(data)
        end_time = time()
        print(repo)
        print('\nSentiment analysis took', round(end_time - start_time, 3), 'seconds to run')
    # '''
