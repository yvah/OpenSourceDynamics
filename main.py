import json
from time import time
from pr_nlu_analysis import Repository

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

    repo.toCSV()

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
