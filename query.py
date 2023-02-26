from classes import newIssueOrPullRequest
from pprint import pprint
from requests import post
import json
from jsonmerge import merge
import os


def run_query(auth, owner, repo, pull_type):

    # list to store each comment
    # issues = []
    # stores the authorisation token and accept
    headers = {
        "Authorization": "token " + auth,
        "Accept": "application/vnd.github+json",
    }

    # for pagination
    has_prev_page = True
    cursor = None
    json_list = []

    print(f"Gathering {pull_type}...")
    # query can only fetch 100 at a time, so keeps fetching until all fetched
    i = 0  # grabs up to 500 queries
    while has_prev_page and i < 1000:
        i += 100
        # gets the query and performs call, on subsequent call passes in cursor for pagination
        query = get_issue_query(owner, repo, pull_type, cursor)
        request = post("https://api.github.com/graphql", json={"query": query}, headers=headers)

        # if api call was successful, adds the comment to the comment list
        if request.status_code == 200:
            # trims the result of the api call to remove unneeded nesting
            # pprint(request.json())
            try:
                trimmed_request = request.json()["data"]["repository"][pull_type]
            except TypeError:
                print("Invalid information provided")
                break
            # pprint(trimmed_request)

            # determines if all comments have been fetched
            has_prev_page = trimmed_request["pageInfo"]["hasPreviousPage"]
            # has_prev_page = False  # TODO remove for pagination
            if has_prev_page:
                cursor = trimmed_request["pageInfo"]["startCursor"]

            # if want to get a list instead of a dictionary:
            # for edge in trimmed_request["edges"]:
            #     issues.append(newIssueOrPullRequest(edge["node"]))
            # gets current working directory
            # creates a folder to store json files, if such doesn't exist
            # if trimmed_request["totalCount"] >= 10:
            json_list += trimmed_request["edges"]

        else:
            print("Invalid information provided")
            return None
        
    cwd = os.getcwd()
    filepath = cwd + "/fetched_data"
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    # creating json object
    # writing data into repoName_pullType.json in cwd/fetched_data directory
    json_string = json.dumps(json_list, indent=4)
    with open(filepath + "/" + f"{repo}_{pull_type}.json", "w") as outfile:
        outfile.write(json_string)
    pprint(json_string)
        
    return json_string


# returns query for issue comments
def get_issue_query(repo, owner, pull_type, cursor=None):

    # for pagination
    if cursor is not None:
        before = f', before: "{cursor}"'
    else:
        before = ""

    query = """
    {
        repository(name: "%s", owner: "%s") {
            %s(last:100,%s states:CLOSED) {
                edges {
                    node {
                        number
                        title
                        author {
                            login
                        }
                        state
                        comments(first:100) {
                            edges {
                                node {
                                    author {
                                        login
                                    }
                                    bodyText
                                    createdAt
                                }
                            }
                            totalCount
                        }
                    }
                }
                pageInfo {
                    hasPreviousPage
                    startCursor
                }
            }
        }
    }
    """ % (repo, owner, pull_type, before)

    return query


# main function for testing code
if __name__ == '__main__':

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
        test = run_query(auth, owner_repo[1], owner_repo[0], pull_type)
        if test:
            pprint(test)
