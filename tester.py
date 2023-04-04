import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

authenticator = IAMAuthenticator('Q4X0jU15o08HYES8jiLwuznIp897uPWzjRiv02CQLu9B')
natural_language_understanding = NaturalLanguageUnderstandingV1(
    version='2022-04-07',
    authenticator=authenticator
)

natural_language_understanding.set_service_url('https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/9aebc290-96c3-478c-8e95-4c250ff5153c%27')

response = natural_language_understanding.analyze(
    url='https://en.wikipedia.org/wiki/Emmanuel_Macron',
    features=Features(sentiment=SentimentOptions(targets=['France']))).get_result()

print(json.dumps(response, indent=2))