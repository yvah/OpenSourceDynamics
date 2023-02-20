import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions
import numpy as np

authenticator = IAMAuthenticator('insert key here')
natural_language_understanding = NaturalLanguageUnderstandingV1(
    version='2022-04-07',
    authenticator=authenticator
)

natural_language_understanding.set_service_url('insert url here')

class Pull_Request:
    def __init__(self, pr):
        self.state = pr['state']
        self.number_of_comments = pr['totalCommentsCount']
        
        comments = ''
        for comment in pr['comments']['edges']:
           comments += comment['node']['bodyText'] + ' '
        self.comments = comments
        
        response = natural_language_understanding.analyze(
            text=self.comments,
            features=Features(sentiment=SentimentOptions())).get_result()
        self.sentiment = response['sentiment']['document']['score']
    
    def __str__(self):
        return "<comments: " + str(self.number_of_comments) + "; state: " + self.state + "; sentiment: " + str(self.sentiment) + ">"

def list_of_pr(data):
    pull_requests = np.array([])
    for pr in data['data']['repository']['pullRequests']['nodes']:
        pull_requests = np.append(pull_requests, Pull_Request(pr))
    return pull_requests

class main:
    f = open('pr_comments.json')
    data = json.load(f)
    
    merged = 0
    merged_sum = 0
    closed = 0
    closed_sum = 0
    pull_requests = list_of_pr(data)
    for pr in pull_requests:
        print(pr)

        if (pr.state == "MERGED"):
            merged_sum += pr.sentiment
            merged+=1
        if (pr.state == "CLOSED"):
            closed_sum += pr.sentiment
            closed+=1

    print('Average sentiment for merged PR:', merged_sum/merged)
    print('Average sentiment for closed PR:', closed_sum/closed)


'''
response = natural_language_understanding.analyze(
    url='https://github.com/flutter/flutter/pull/120984',
    features=Features(sentiment=SentimentOptions(targets=['Pull Request']))).get_result()

print(json.dumps(response, indent=2))
'''
