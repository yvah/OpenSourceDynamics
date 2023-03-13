from pprint import pprint
from requests import post
import json
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
    has_next_page = True
    cursor = None
    json_list = []
    print(f"Gathering {pull_type}...")

    # query can only fetch 100 at a time, so keeps fetching until all fetched
    # inner loop does the same with comments
    i = 0  # grabs up to 1000 queries
    while has_next_page and i < 1000:
        i += 100

        # forms the query and performs call, on subsequent iterations passes in cursor for pagination
        query = get_query(owner, repo, pull_type, "CLOSED", cursor)
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
            has_next_page = trimmed_request["pageInfo"]["hasNextPage"]
            if has_next_page:
                cursor = trimmed_request["pageInfo"]["endCursor"]

            # if want to get a list instead of a dictionary:
            # for edge in trimmed_request["edges"]:
            # issues.append(newIssueOrPullRequest(edge["node"]))
            # gets current working directory
            # creates a folder to store json files, if such doesn't exist
            # if trimmed_request["totalCount"] >= 10:

            for node in trimmed_request["edges"]:
                if node["node"]["comments"]["totalCount"] >= 10:
                    json_list.append(node)

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
def get_query(repo, owner, p_type, state, outer_cursor=None):

    # for pagination
    if outer_cursor is not None:
        start_point = f', after: "{outer_cursor}"'
    else:
        start_point = ""

    query = """
    {
        repository(name: "%s", owner: "%s") {
            %s(first:100,%s states:%s) {
                edges {
                    node {
                        number
                        title
                        author {
                            login
                        }
                        state
                        comments(first:100) {
                            totalCount
                            edges {
                                node {
                                    author {
                                        login
                                    }
                                    bodyText
                                    createdAt
                                }
                            }
                        }
                    }
                }
                pageInfo {
                    hasNextPage
                    endCursor
                }
            }
        }
    }
    """ % (repo, owner, p_type, start_point, state)

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
            print(len(test))
