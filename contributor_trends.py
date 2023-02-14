import numpy as np
import json

def list_of_contributors(data):
    contributors = np.array([])
    for contributor in data['contributors']:
        contributors = np.append(contributors, contributor['username'])
    return contributors

# this will change based on how the data apears in the json file
def get_country(location):
    return location[location.find(",")+2:]

def frequency_of_countries(data):
    countries = np.array([])
    for i in data['contributors']:
        countries = np.append(countries, get_country(i["location"]))
    countries = np.unique(countries, return_counts=True)
    return countries

def print_country_frequency(countries):
    countries = np.vstack((countries[0], countries[1])).T
    return countries

def geographic_diversity(countries):
    n = np.sum(countries[1])
    D = 1-np.sum((countries[1]/n)**2)
    if (D < 0.25):
        print("Contributors are not geographically diverse")
    if (D < 0.5):
        print("Contributors are somewhat not geographically diverse")
    if (D < 0.75):
        print("Contributors are somewhat geographically diverse")
    else:
        print("Contributors are very geographically diverse")
    return D

def get_email_domain(email):
    return email[email.find("@"):]

def email_domains(data):
    domains = np.array([])
    for i in data['contributors']:
        domains = np.append(domains, get_email_domain(i["email"]))
    return domains

class main:
    f = open('example_contributor_data.json')
    data = json.load(f)

    print("\n\n")
    
    contributors = list_of_contributors(data)
    print("List of contributors:", contributors)
    print("Number of contributors:", np.size(contributors))
    
    emails = email_domains(data)
    print("Email domains:\n", emails)
    
    countries = frequency_of_countries(data)
    print("Frequency of countries:\n", print_country_frequency(countries))
    print(geographic_diversity(countries))

    print("\n\n")

    f.close()
