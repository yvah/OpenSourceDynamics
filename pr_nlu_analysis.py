import json, requests, os, csv
import statistics
from time import time
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions, EmotionOptions, ConceptsOptions
import scipy.stats as stats
from datetime import datetime


# Pulls API Keys from keys.txt file
keys = open('credentials/keys.txt', 'r')
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
    def __init__(self, data, type):
        # Create list of RepoItem objects
        self.repo_items = list_of_repo_items(data)

        # Defines values for state and gender
        self.values_state = ['Open', 'Closed', '']
        self.values_gender = ['Female', 'Male', 'Unknown']

        # Calculate averages
        self.average_sentiment = average(self.repo_items, 'Sentiment', 'None')[0]
        self.average_sentiment_gender = average(self.repo_items, 'Sentiment', 'Gender')
        em_av = [average(self.repo_items, 'Sadness', 'None'),
                 average(self.repo_items, 'Joy', 'None'),
                 average(self.repo_items, 'Fear', 'None'),
                 average(self.repo_items, 'Disgust', 'None'),
                 average(self.repo_items, 'Anger', 'None')]
        self.average_emotion = [em_av[0][0], em_av[1][0], em_av[2][0], em_av[3][0], em_av[4][0]]
        self.average_emotion_gender = [average(self.repo_items, 'Sadness', 'Gender'),
                                       average(self.repo_items, 'Joy', 'Gender'),
                                       average(self.repo_items, 'Fear', 'Gender'),
                                       average(self.repo_items, 'Disgust', 'Gender'),
                                       average(self.repo_items, 'Anger', 'Gender')]
        self.average_lifetime = average(self.repo_items, 'Lifetime', 'None')[0]
        self.average_lifetime_gender = average(self.repo_items, 'Lifetime', 'Gender')

        # Calculate frequencies
        self.freq_state = frequency(self.repo_items, 'State')
        self.freq_gender = frequency(self.repo_items, 'Gender')

        # Calculate correlation
        self.corr_gender_comments = point_biserial_correlation_test(self.repo_items, 'Gender', 'Comments')
        self.corr_gender_sentiment = point_biserial_correlation_test(self.repo_items, 'Gender', 'Sentiment')
        self.corr_gender_lifetime = point_biserial_correlation_test(self.repo_items, 'Gender', 'Lifetime')
        self.corr_gender_emotion = [point_biserial_correlation_test(self.repo_items, 'Gender', 'Sadness'),
                                    point_biserial_correlation_test(self.repo_items, 'Gender', 'Joy'),
                                    point_biserial_correlation_test(self.repo_items, 'Gender', 'Fear'),
                                    point_biserial_correlation_test(self.repo_items, 'Gender', 'Disgust'),
                                    point_biserial_correlation_test(self.repo_items, 'Gender', 'Anger')]
        self.corr_comments_sentiment = pearson_correlation_test(self.repo_items, 'Comments', 'Sentiment')
        self.corr_comments_emotion = [pearson_correlation_test(self.repo_items, 'Comments', 'Sadness'),
                                      pearson_correlation_test(self.repo_items, 'Comments', 'Joy'),
                                      pearson_correlation_test(self.repo_items, 'Comments', 'Fear'),
                                      pearson_correlation_test(self.repo_items, 'Comments', 'Disgust'),
                                      pearson_correlation_test(self.repo_items, 'Comments', 'Anger')]
        self.corr_lifetime_sentiment = pearson_correlation_test(self.repo_items, 'Lifetime', 'Sentiment')
        self.corr_lifetime_emotion = [pearson_correlation_test(self.repo_items, 'Lifetime', 'Sadness'),
                                      pearson_correlation_test(self.repo_items, 'Lifetime', 'Joy'),
                                      pearson_correlation_test(self.repo_items, 'Lifetime', 'Fear'),
                                      pearson_correlation_test(self.repo_items, 'Lifetime', 'Disgust'),
                                      pearson_correlation_test(self.repo_items, 'Lifetime', 'Anger')]

        # Additional statistics for Pull Requests
        if type == 'pullRequests':
            self.values_state = ['Open', 'Closed', 'Merged']
            self.average_lifetime_state = average(self.repo_items, 'Lifetime', 'State')
            self.average_sentiment_state = average(self.repo_items, 'Sentiment', 'State')
            self.average_emotion_state = [average(self.repo_items, 'Sadness', 'State'),
                                      average(self.repo_items, 'Joy', 'State'),
                                      average(self.repo_items, 'Fear', 'State'),
                                      average(self.repo_items, 'Disgust', 'State'),
                                      average(self.repo_items, 'Anger', 'State')]
            self.corr_state_gender = chi_square_correlation_test(self.repo_items)
            self.corr_state_comments = point_biserial_correlation_test(self.repo_items, 'State', 'Comments')
            self.corr_state_sentiment = point_biserial_correlation_test(self.repo_items, 'State', 'Sentiment')
            self.corr_state_lifetime = point_biserial_correlation_test(self.repo_items, 'State', 'Lifetime')
            self.corr_state_emotion = [point_biserial_correlation_test(self.repo_items, 'State', 'Sadness'),
                                   point_biserial_correlation_test(self.repo_items, 'State', 'Joy'),
                                   point_biserial_correlation_test(self.repo_items, 'State', 'Fear'),
                                   point_biserial_correlation_test(self.repo_items, 'State', 'Disgust'),
                                   point_biserial_correlation_test(self.repo_items, 'State', 'Anger')]
        else:
            self.average_lifetime_state = [None, None, None]
            self.average_sentiment_state = [None, None, None]
            self.average_emotion_state = [[None, None, None], [None, None, None], [None, None, None], [None, None, None], [None, None, None]]
            self.corr_state_gender = [None, None]
            self.corr_state_comments = [None, None]
            self.corr_state_sentiment = [None, None]
            self.corr_state_lifetime = [None, None]
            self.corr_state_emotion = [[None, None], [None, None], [None, None], [None, None], [None, None]]

    def to_csv(self):
        folder = f'{os.getcwd()}/fetched_data/nlu_results/'
        with open(f'{folder}repo_items.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, ['Number', 'Title', 'Author', 'Gender', 'State', 'Created', 'Closed', 'Lifetime', 'Number of Comments',
                                        'Sentiment', 'Sadness', 'Joy', 'Fear', 'Disgust', 'Anger', 'Concepts'])
            writer.writeheader()
            for ri in self.repo_items:
                analysis_result = [
                    {
                        'Number': ri.number,
                        'Title': ri.title,
                        'Author': ri.author,
                        'Gender': ri.gender,
                        'State': ri.state,
                        'Created': ri.createdAt,
                        'Closed': ri.closedAt,
                        'Lifetime': ri.lifetime,
                        'Number of Comments': ri.number_of_comments,
                        'Sentiment': ri.sentiment,
                        'Sadness': ri.emotion[0][1],
                        'Joy': ri.emotion[1][1],
                        'Fear': ri.emotion[2][1],
                        'Disgust': ri.emotion[3][1],
                        'Anger': ri.emotion[4][1],
                        'Concepts': str(ri.concepts)[1:-1]
                    }
                ]
                writer.writerows(analysis_result)

        with open(f'{folder}averages.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Sentiment Average', 'Sadness Average', 'Joy Average', 'Fear Average', 'Disgust Average', 'Anger Average', 'Lifetime Average'])
            writer.writerow([self.average_sentiment, self.average_emotion[0], self.average_emotion[1], self.average_emotion[2], self.average_emotion[3], self.average_emotion[4], self.average_lifetime])
        
        with open(f'{folder}state.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['State Values', 'State Frequency', 'State-Sentiment Average', 'State-Sadness Averages', 'State-Joy Averages', 'State-Fear Averages', 'State-Disgust Averages', 'State-Anger Averages', 'State-Lifetime Average'])
            for i in range(3):
                writer.writerow([self.values_state[i], self.freq_state[i], self.average_sentiment_state[i], self.average_emotion_state[0][i], self.average_emotion_state[1][i], self.average_emotion_state[2][i], self.average_emotion_state[3][i], self.average_emotion_state[4][i], self.average_lifetime_state[i]])
        
        with open(f'{folder}gender.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Gender Values', 'Gender Frequency', 'Gender-Sentiment Average', 'Gender-Sadness Averages', 'Gender-Joy Averages', 'Gender-Fear Averages', 'Gender-Disgust Averages', 'Gender-Anger Averages', 'Gender-Lifetime Average'])
            for i in range(3):
                writer.writerow([self.values_gender[i], self.freq_gender[i], self.average_sentiment_gender[i], self.average_emotion_gender[0][i], self.average_emotion_gender[1][i], self.average_emotion_gender[2][i], self.average_emotion_gender[3][i], self.average_emotion_gender[4][i], self.average_lifetime_gender[i]])

        with open(f'{folder}correlations.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, ['Correlation', 'State-Gender Correlation', 
                                        'State-Comments Correlation', 'State-Lifetime Correlation', 'State-Sentiment Correlation', 
                                        'State-Sadness Correlation', 'State-Joy Correlation', 'State-Fear Correlation', 'State-Disgust Correlation', 'State-Anger Correlation', 
                                        'Gender-Comments Correlation', 'Gender-Lifetime Correlation', 'Gender-Sentiment Correlation', 
                                        'Gender-Sadness Correlation', 'Gender-Joy Correlation', 'Gender-Fear Correlation', 'Gender-Disgust Correlation', 'Gender-Anger Correlation', 
                                        'Comments-Sentiment Correlation', 
                                        'Comments-Sadness Correlation', 'Comments-Joy Correlation', 'Comments-Fear Correlation', 'Comments-Disgust Correlation', 'Comments-Anger Correlation', 
                                        'Lifetime-Sentiment Correlation', 
                                        'Lifetime-Sadness Correlation', 'Lifetime-Joy Correlation', 'Lifetime-Fear Correlation', 'Lifetime-Disgust Correlation', 'Lifetime-Anger Correlation'])
            writer.writeheader()
            for i in range(2):
                analysis_result = [
                    {
                        'Correlation': f'{"p-value" if i == 0 else "test statistic"}',
                        'State-Gender Correlation': self.corr_state_gender[i],
                        'State-Comments Correlation': self.corr_state_comments[i],
                        'State-Lifetime Correlation': self.corr_state_lifetime[i],
                        'State-Sentiment Correlation': self.corr_state_sentiment[i],
                        'State-Sadness Correlation': self.corr_state_emotion[0][i], 
                        'State-Joy Correlation': self.corr_state_emotion[1][i], 
                        'State-Fear Correlation': self.corr_state_emotion[2][i], 
                        'State-Disgust Correlation': self.corr_state_emotion[3][i], 
                        'State-Anger Correlation': self.corr_state_emotion[4][i], 
                        'Gender-Comments Correlation': self.corr_gender_comments[i],
                        'Gender-Lifetime Correlation': self.corr_gender_lifetime[i],
                        'Gender-Sentiment Correlation': self.corr_gender_sentiment[i],
                        'Gender-Sadness Correlation': self.corr_gender_emotion[0][i], 
                        'Gender-Joy Correlation': self.corr_gender_emotion[1][i], 
                        'Gender-Fear Correlation': self.corr_gender_emotion[2][i], 
                        'Gender-Disgust Correlation': self.corr_gender_emotion[3][i], 
                        'Gender-Anger Correlation': self.corr_gender_emotion[4][i], 
                        'Comments-Sentiment Correlation': self.corr_comments_sentiment[i],
                        'Comments-Sadness Correlation': self.corr_comments_emotion[0][i], 
                        'Comments-Joy Correlation': self.corr_comments_emotion[1][i], 
                        'Comments-Fear Correlation': self.corr_comments_emotion[2][i], 
                        'Comments-Disgust Correlation': self.corr_comments_emotion[3][i], 
                        'Comments-Anger Correlation': self.corr_comments_emotion[4][i],
                        'Lifetime-Sentiment Correlation': self.corr_lifetime_sentiment[i], 
                        'Lifetime-Sadness Correlation': self.corr_lifetime_emotion[0][i], 
                        'Lifetime-Joy Correlation': self.corr_lifetime_emotion[1][i], 
                        'Lifetime-Fear Correlation': self.corr_lifetime_emotion[2][i], 
                        'Lifetime-Disgust Correlation': self.corr_lifetime_emotion[3][i], 
                        'Lifetime-Anger Correlation': self.corr_lifetime_emotion[4][i]
                    }
                ]
                writer.writerows(analysis_result)

    def __str__(self):
        result = ''
        # Print RepoItems
        for ri in self.repo_items:
            result += str(ri) + '\n'
        result += '\n'

        # Print averages
        result += str(self.average_sentiment) + '\n'
        result += str(self.average_sentiment_state) + '\n'
        result += str(self.average_sentiment_gender) + '\n'
        result += str(self.average_emotion) + '\n'
        result += str(self.average_emotion_state) + '\n'
        result += str(self.average_emotion_gender) + '\n'

        # Print frequencies
        result += str(self.freq_state) + '\n'
        result += str(self.freq_gender) + '\n\n'
        
        return result


# Defines pull requests and issues as objects
class RepoItem:
    # Constructor takes in a json node representing a pr
    def __init__(self, ri):
        self.number = ri['number']
        self.title = ri['title']
        self.state = ri['state']

        self.createdAt = ri['createdAt'].replace('T', ' ').replace('Z', '')
        self.closedAt = None
        self.lifetime = None
        if self.state != 'OPEN':
            self.closedAt = ri['closedAt'].replace('T', ' ').replace('Z', '')
            datetimeFormat = '%Y-%m-%d %H:%M:%S'
            self.lifetime = round((datetime.strptime(self.closedAt, datetimeFormat) - datetime.strptime(self.createdAt,datetimeFormat)).total_seconds() / 3600.0)
        self.number_of_comments = ri['commentCount']
        self.author = ri['author'].split()[0]
        self.gender = getGender(self.author)

        # NEEDS TO CHANGE
        # Takes all comments and concatenates into single string -> not efficient
        comments = ''
        for comment in ri['comments']:
            comments += comment['bodyText'] + ' '
        self.comments = comments

        # IBM NLP
        response = natural_language_understanding.analyze(
            text=self.comments,
            features=Features(sentiment=SentimentOptions(), emotion=EmotionOptions(), concepts=ConceptsOptions(limit=3))).get_result()
        
        # Store Sentiment Analysis result
        self.sentiment = round(response['sentiment']['document']['score'], 4)
        
        # Creates an array to store emotion scores
        self.emotion = [['sadness', 0], ['joy', 0], ['fear', 0], ['disgust', 0], ['anger', 0]]
        for i in range(5):
            self.emotion[i][1] = round(response['emotion']['document']['emotion'][self.emotion[i][0]], 4)

        # Store concepts
        self.concepts = []
        for i in range(3):
            con = response['concepts']
            if con[i]['relevance'] > 0.7:
                self.concepts.append(con[i]['text']) 
        if not self.concepts:
            self.concepts = [None]

    # Defines a print method for RepoItem
    def __str__(self):
        return "<state: " + self.state + "; comments: " + str(self.number_of_comments) + "; sentiment: " + str(self.sentiment) + "; author: " + self.author + "; gender: " + self.gender + "; lifetime: " + str(self.lifetime) + "; concepts: " + str(self.concepts)[1:-1] + ">"


# Takes a json file and parses it into a list of RepoItem objects
def list_of_repo_items(data):
    repo_items = []
    for ri in data:
        # NEED TO IMPLEMENT BETTER ERROR HANDLING
        # ApiException: Error: not enough text for language id, Code: 422
        try:
            repo_items.append(RepoItem(ri))
        except Exception:
            pass
    return repo_items


# Get averages for different variables and filters
def average(repo_items, variable, filter):
    list1 = []
    list2 = []
    list3 = []

    for ri in repo_items:
        if variable == 'Lifetime' and ri.state == 'OPEN':
            continue

        filter_var = ''
        if filter == 'State':
            filter_var = ri.state
        elif filter == 'Gender':
            filter_var = ri.gender
        if filter == 'None':
            filter_var = 'None'

        if variable == 'Sentiment':
            var = ri.sentiment
        elif variable == 'Lifetime':
            var = ri.lifetime
        elif variable == 'Sadness':
            var = ri.emotion[0][1]
        elif variable == 'Joy':
            var = ri.emotion[1][1]
        elif variable == 'Fear':
            var = ri.emotion[2][1]
        elif variable == 'Disgust':
            var = ri.emotion[3][1]
        elif variable == 'Anger':
            var = ri.emotion[4][1]

        if filter_var == 'OPEN' or filter_var == 'female' or filter_var == 'None':
            list1.append(var)
        elif filter_var == 'CLOSED' or filter_var == 'male':
            list2.append(var)
        else:
            list3.append(var)

    return [None if not list1 else round(statistics.fmean(list1), 4),
            None if not list2 else round(statistics.fmean(list2), 4),
            None if not list3 else round(statistics.fmean(list3), 4)]


# Get frequencies for different variables
def frequency(repo_items, variable):
    list = [0, 0, 0]
    for ri in repo_items:
        var = ''
        if (variable == 'State'):
            var = ri.state
        elif (variable == 'Gender'):
            var = ri.gender

        if var == 'OPEN' or var == 'female':
            list[0] += 1
        elif var == 'CLOSED' or var == 'male':
            list[1] += 1
        else:
            list[2] += 1

    return list


# Preforms a Point-Biserial Correlation test
def point_biserial_correlation_test(repo_items, di_var, cont_var):
    di_list = []
    cont_list = []
    for ri in repo_items:
        if cont_var == 'Lifetime' and ri.state == 'OPEN':
            continue

        di_value = ''
        if di_var == 'State':
            di_value = ri.state
        elif di_var == 'Gender':
            di_value = ri.gender

        if di_value == 'MERGED' or di_value == 'female':
            di_list.append(0)
        elif di_value == 'CLOSED' or di_value == 'male':
            di_list.append(1)
        else:
            continue

        if cont_var == 'Sentiment':
            cont_list.append(ri.sentiment)
        elif cont_var == 'Lifetime':
            cont_list.append(ri.lifetime)
        elif cont_var == 'Comments':
            cont_list.append(ri.number_of_comments)
        elif cont_var == 'Sadness':
            cont_list.append(ri.emotion[0][1])
        elif cont_var == 'Joy':
            cont_list.append(ri.emotion[1][1])
        elif cont_var == 'Fear':
            cont_list.append(ri.emotion[2][1])
        elif cont_var == 'Disgust':
            cont_list.append(ri.emotion[3][1])
        elif cont_var == 'Anger':
            cont_list.append(ri.emotion[4][1])

    try:
        result = stats.pointbiserialr(di_list, cont_list)
        return [round(result.pvalue, 4), round(result.statistic, 4)]
    except:
        return [None, None]


# Preforms a Chi-Square Correlation test
def chi_square_correlation_test(repo_items):
    list = [[0, 0], [0, 0], [0, 0]]
    for ri in repo_items:
        if ri.gender == 'female':
            if ri.state == 'MERGED':
                list[0][0] += 1
            elif ri.state == 'CLOSED':
                list[0][1] += 1
        elif ri.gender == 'male':
            if ri.state == 'MERGED':
                list[1][0] += 1
            elif ri.state == 'CLOSED':
                list[1][1] += 1
        else:
            if ri.state == 'MERGED':
                list[2][0] += 1
            elif ri.state == 'CLOSED':
                list[2][1] += 1
    try:
        result = stats.chi2_contingency(list)
        return [round(result.pvalue, 4), round(result.statistic, 4)]
    except:
        return [None, None]


# Preforms a Pearson Correlation test
def pearson_correlation_test(repo_items, var1, var2):
    var1_list = []
    var2_list = []

    for ri in repo_items:
        if var1 == 'Lifetime' and ri.state == 'OPEN':
            continue

        if var1 == 'Comments':
            var1_list.append(ri.number_of_comments)
        elif var1 == 'Lifetime':
            var1_list.append(ri.lifetime)

        if var2 == 'Sentiment':
            var2_list.append(ri.sentiment)
        elif var2 == 'Sadness':
            var2_list.append(ri.emotion[0][1])
        elif var2 == 'Joy':
            var2_list.append(ri.emotion[1][1])
        elif var2 == 'Fear':
            var2_list.append(ri.emotion[2][1])
        elif var2 == 'Disgust':
            var2_list.append(ri.emotion[3][1])
        elif var2 == 'Anger':
            var2_list.append(ri.emotion[4][1])

    try:
        result = stats.pearsonr(var1_list, var2_list)
        return [round(result.pvalue, 4), round(result.statistic, 4)]
    except:
        return [None, None]


# Predicts gender of a given name using genderize.io API
def getGender(name):
    url = ""
    cnt = 0

    if url == "":
        url = "name[0]=" + name
    else:
        cnt += 1
        url = url + "&name[" + str(cnt) + "]=" + name

    req = requests.get("https://api.genderize.io?" + url)
    # if request limit reached, label as unknown
    if req.status_code != 429:
        result = json.loads(req.text)
        gender = result[0]["gender"]
        if gender is not None:
            return gender
    return "unknown"
