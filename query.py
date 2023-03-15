from pprint import pprint
from requests import post
import json
import os
from time import time


comment_threshold = 10
pull_rate = 100  # maximum possible value is 100
max_iterations = -1  # number of iterations that should run; -1 to keep going until all issues/prs fetched


# for timing how long it takes a function to run
def time_execution(function):
    def wrapper(*args):
        start_time = time()
        value = function(*args)
        end_time = time()
        print(f"{function.__name__} took {round(end_time - start_time, 3)} seconds to run")
        return value
    return wrapper


@time_execution
def run_query(auth, owner, repo, pull_type):

    print(f"Gathering {pull_type}...")

    # final list to be returned
    json_list = []
    # stores the authorisation token and accept
    headers = {
        "Authorization": "token " + auth,
        "Accept": "application/vnd.github+json",
    }

    # for pagination
    has_next_page = True
    cursor = None

    i = 0
    # query can only fetch at most 100 at a time, so keeps fetching until all fetched
    while has_next_page and i != max_iterations:
        i += 1

        # forms the query and performs call, on subsequent iterations passes in cursor for pagination
        query = get_comments_query(repo, owner, pull_type, cursor)
        try:
            request = post("https://api.github.com/graphql", json={"query": query}, headers=headers)
        except Exception:
            print(f"error at iteration {i}")
            i -= 1
            continue
        # temp = request.json()

        # if api call was successful, adds the comment to the comment list
        if request.status_code == 200:
            try:
                # trims the result of the api call to remove unneeded nesting
                trimmed_request = request.json()["data"]["repository"][pull_type]
            except TypeError:
                if json_list is not None:
                    pprint(json_list)
                print("Invalid information provided")
                break
            # pprint(trimmed_request)

            # determines if all issues/prs have been fetched
            has_next_page = trimmed_request["pageInfo"]["hasNextPage"]
            if has_next_page:
                cursor = trimmed_request["pageInfo"]["endCursor"]

            # filters out issues/prs with under the threshold of comments, comments made by bots
            # also ensures all comments over 100 are fetched
            filtered_request = filter_request(trimmed_request, repo, owner, pull_type[0:-1], headers)
            json_list.append(filtered_request)  # add to final list

        else:
            print(f"Status code: {str(request.status_code)} on iteration {i}. Retrying")
            i -= 1

    json_string = json.dumps(json_list, indent=4)
    write_to_file(json_string, repo, pull_type)
    # pprint(json_string)
    return json_string


def filter_request(request, repo, owner, p_type, headers):

    return_list = []
    # iterates through issue/pr, only adds it to json_list if it has over the threshold of comments
    for node in request["edges"]:
        comments = node["node"]["comments"]
        if comments["totalCount"] >= comment_threshold:
            # determines if the issue/pr has over 100 comments
            # if it does, it fetches the rest of them and appends them to the first 100 comments
            if comments["pageInfo"]["hasNextPage"]:
                comments["edges"] += get_other_comments(node["node"]["number"],
                                                        comments["pageInfo"]["endCursor"],
                                                        repo, owner, p_type, headers)
            comments.pop("pageInfo")  # pageInfo no longer needed, so removed from dict

            # iterates through each comment removes it if it was made by a bot
            for i, comment in enumerate(comments["edges"]):
                try:
                    if comment["node"]["author"]["__typename"] == "Bot":
                        comments["edges"].pop(i)
                        comments["totalCount"] -= 1
                except TypeError:
                    # if account deleted, author will be None so give it login deletedUser
                    comment["node"]["author"] = {'login': 'deletedUser'}
            return_list.append(node)

    return return_list


# writes a json_string out to a file
def write_to_file(json_string, repo, p_type):
    cwd = os.getcwd()
    filepath = cwd + "/fetched_data"
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    # writing data into repoName_pullType.json in cwd/fetched_data directory
    with open(filepath + "/" + f"{repo}_{p_type}.json", "w") as outfile:
        outfile.write(json_string)


# if over 100 comments, fetches the rest of them
def get_other_comments(number, cursor, repo, owner, p_type, headers):

    # for pagination
    has_next_page = True
    comment_list = None

    # query can only fetch at most 100 at a time, so keeps fetching until all fetched
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
        """ % (repo, owner, p_type, pull_rate, start_point)

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
        # if test:
        #     pprint(test)
