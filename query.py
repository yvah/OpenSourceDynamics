from pprint import pprint
from requests import post
import json
import os


comment_threshold = 10
max_pull_rate = 100


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
    highest_count = 0
    print(f"Gathering {pull_type}...")

    # query can only fetch 100 at a time, so keeps fetching until all fetched
    i = 0  # performs 10 requests
    while has_next_page and i < 10:
        i += 1

        # forms the query and performs call, on subsequent iterations passes in cursor for pagination
        query = get_comments_query(repo, owner, pull_type, cursor)
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
                comments = node["node"]["comments"]
                if comments["totalCount"] >= comment_threshold:
                    if comments["pageInfo"]["hasNextPage"]:
                        comments["edges"] += get_other_comments(node["node"]["number"],
                                                                comments["pageInfo"]["endCursor"],
                                                                owner, repo, pull_type[0:-1], headers)
                    for i, comment in enumerate(comments["edges"]):
                        if comment["node"]["author"]["__typename"] == "Bot":
                            comments["edges"].pop(i)
                            comments["totalCount"] -= 1
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


# if over 100 comments, fetches the rest of them
def get_other_comments(number, cursor, owner, repo, p_type, headers):

    # for pagination
    has_next_page = True
    comment_list = None

    # query can only fetch 100 at a time, so keeps fetching until all fetched
    i = 0  # grabs up to 1000 queries
    while has_next_page:

        # forms the query and performs call, on subsequent iterations passes in cursor for pagination
        query = get_ind_query(repo, owner, number, p_type, cursor)
        request = post("https://api.github.com/graphql", json={"query": query}, headers=headers)

        # if api call was successful, adds the comment to the comment list
        if request.status_code == 200:
            # trims the result of the api call to remove unneeded nesting
            # pprint(request.json())
            temp = request.json()
            try:
                comments = request.json()["data"]["repository"][p_type]["comments"]
            except TypeError:
                print("Invalid information provided")
                break
            # pprint(trimmed_request)

            # determines if all comments have been fetched
            has_next_page = comments["pageInfo"]["hasNextPage"]
            if has_next_page:
                cursor = comments["pageInfo"]["endCursor"]

            if comment_list is None:
                comment_list = comments["edges"]
            else:
                comment_list += comments["edges"]

    return comment_list


# returns query for individual comments
def get_ind_query(repo, owner, number, p_type, cursor=None):

    # for pagination
    if cursor is not None:
        start_point = f', after: "{cursor}"'
    else:
        start_point = ""

    query = """
    {
        repository(name: "%s", owner: "%s") {
            %s(number: %d) {
                comments(first:100%s) {
                    edges {
                        node {
                            author {
                                login
                                __typename
                            }
                            bodyText
                            createdAt
                        }
                    }
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                }
            }
        }  
    }
    """ % (repo, owner, p_type, number, start_point)

    return query


# returns query for issue or pull request comments
def get_comments_query(repo, owner, p_type, cursor=None):
    # for pagination
    if cursor is not None:
        start_point = f', after: "{cursor}"'
    else:
        start_point = ""

    query = """
        {
            repository(name: "%s", owner: "%s") {
                %s(first:%d,%s) {
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
                                            __typename
                                        }
                                        bodyText
                                        createdAt
                                    }
                                }
                                pageInfo {
                                    hasNextPage
                                    endCursor
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
        """ % (repo, owner, p_type, max_pull_rate, start_point)

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
        test = run_query(auth, owner_repo[0], owner_repo[1], pull_type)
        if test:
            pprint(test)
            print(len(test))
