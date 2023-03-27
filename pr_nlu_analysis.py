import json, requests, os, csv
import statistics
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

        # Calculate averages
        self.average_sentiment = average(self.pull_requests, 'Sentiment', 'None')
        self.average_sentiment_state = average(self.pull_requests, 'Sentiment', 'State')
        self.average_sentiment_gender = average(self.pull_requests, 'Sentiment', 'Gender')
        self.average_emotion = [average(self.pull_requests, 'Sadness', 'None'), 
                                  average(self.pull_requests, 'Joy', 'None'),
                                  average(self.pull_requests, 'Fear', 'None'),
                                  average(self.pull_requests, 'Disgust', 'None'),
                                  average(self.pull_requests, 'Anger', 'None')]
        self.average_emotion_state = [average(self.pull_requests, 'Sadness', 'State'), 
                                  average(self.pull_requests, 'Joy', 'State'),
                                  average(self.pull_requests, 'Fear', 'State'),
                                  average(self.pull_requests, 'Disgust', 'State'),
                                  average(self.pull_requests, 'Anger', 'State')]
        self.average_emotion_gender = [average(self.pull_requests, 'Sadness', 'Gender'), 
                                  average(self.pull_requests, 'Joy', 'Gender'),
                                  average(self.pull_requests, 'Fear', 'Gender'),
                                  average(self.pull_requests, 'Disgust', 'Gender'),
                                  average(self.pull_requests, 'Anger', 'Gender')]

        # Preform Point Biserial test
        self.p_value = self.r_value = None
        #if self.merged_average is not None and self.closed_average is not None:
        point_biserial = correlation_test(self.pull_requests)
        self.p_value = round(point_biserial.pvalue, 4)
        self.r_value = round(point_biserial.statistic, 4)
    
    def toCSV(self):
        cwd = os.getcwd()
        csv_fields = ['Number', 'Title', 'Author', 'Gender', 'State', 'Created', 'Closed', 'Number of Comments', 'Sentiment', 'Sadness', 'Joy', 'Fear', 'Disgust', 'Anger']
        with open(f'{cwd}/fetched_data/sentiment_analysis_result.csv', 'w', newline='') as analysis_results_file:
            writer = csv.DictWriter(analysis_results_file, csv_fields)
            writer.writeheader()
            for pr in self.pull_requests:
                analysis_result = [
                    {
                        'Number': f'{str(pr.number)}',
                        'Title': f'{str(pr.title)}',
                        'Author': f'{str(pr.author)}',
                        'Gender': f'{str(pr.gender)}',
                        'State': f'{str(pr.state)}',
                        'Created': f'{str(pr.createdAt)}',
                        'Closed': f'{str(pr.closedAt)}',
                        'Number of Comments': f'{str(pr.number_of_comments)}',
                        'Sentiment': f'{str(pr.sentiment)}',
                        'Sadness': f'{str(pr.emotion[0][1])}',
                        'Joy': f'{str(pr.emotion[1][1])}',
                        'Fear': f'{str(pr.emotion[2][1])}',
                        'Disgust': f'{str(pr.emotion[3][1])}',
                        'Anger': f'{str(pr.emotion[4][1])}'
                    }
                ] 
                writer.writerows(analysis_result)

    def __str__(self):
        result = ''
        # Print PullRequests
        for pr in self.pull_requests:
            result += str(pr) + '\n'
        result += '\n'

        # Print averages
        '''
        if self.merged_average is None:
            result += 'No merged PR\n'
        else:
            result += 'Average sentiment for merged PR: ' + str(self.merged_average) + '\n'
        if self.closed_average is None:
            result += 'No closed PR\n'
        else:
            result += 'Average sentiment for closed PR: ' + str(self.closed_average) + '\n'
        result += '\n'
        '''
        result += str(self.average_sentiment) + '\n'
        result += str(self.average_sentiment_state) + '\n'
        result += str(self.average_sentiment_gender) + '\n'
        result += str(self.average_emotion) + '\n'
        result += str(self.average_emotion_state) + '\n'
        result += str(self.average_emotion_gender) + '\n'

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
        self.number = pr['number']
        self.title = pr['title']
        self.closedAt = pr['closedAt']
        self.createdAt = pr['createdAt']
        self.state = pr['state']
        self.number_of_comments = pr['commentCount']
        self.author = pr['author'].split()[0]
        self.gender = getGender(self.author)

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
        #s = str(self.emotion)
        return "<state: " + self.state + "; comments: " + str(self.number_of_comments) + "; sentiment: " + str(
            self.sentiment) + "; author: " + self.author + "; gender: " + self.gender + ">"


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

# Get averages for different variables and filters
def average(pull_requests, variable, filter):
    list1 = []
    list2 = []
    list3 = []

    for pr in pull_requests:
        if (filter == 'State'):
            filter_var = pr.state
        elif (filter == 'Gender'):
            filter_var = pr.gender
        if filter == 'None':
            filter_var = 'None'

        if variable == 'Sentiment':
            var = pr.sentiment
        elif variable == 'Sadness':
            var = pr.emotion[0][1]
        elif variable == 'Joy':
            var = pr.emotion[1][1]
        elif variable == 'Fear':
            var = pr.emotion[2][1]
        elif variable == 'Disgust':
            var = pr.emotion[3][1]
        elif variable == 'Anger':
            var = pr.emotion[4][1]
        
        if filter_var == 'MERGED' or filter_var == 'female' or filter_var == 'None':
            list1.append(var)
        elif filter_var == 'CLOSED' or filter_var == 'male':
            list2.append(var)
        else:
            list3.append(var)
    
    return [None if not list1 else round(statistics.fmean(list1), 4), 
            None if not list2 else round(statistics.fmean(list2), 4),
            None if not list3 else round(statistics.fmean(list3), 4)]

def frequency(pull_requests, variable):
    list = [0, 0, 0]
    for pr in pull_requests:
        if (filter == 'State'):
            var = pr.state
        elif (filter == 'Gender'):
            var = pr.gender
        
        if var == 'MERGED' or var == 'female' or var == 'None':
            list[0] += 1
        elif var == 'CLOSED' or var == 'male':
            list[1] += 1
        else:
            list[2] += 1
    
    return list

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

def getGender(name):
	url = ""
	cnt = 0
        
	if url == "":
		url = "name[0]=" + name
	else:
		cnt += 1
		url = url + "&name[" + str(cnt) + "]=" + name

	req = requests.get("https://api.genderize.io?" + url)
	result = json.loads(req.text)
	gender = result[0]["gender"]
	if gender is None:
		return "none"
	return gender