from pprint import pprint
from requests import post
import json
import os
from time import time

comment_threshold = 10
max_iterations = -1  # number of iterations that should run; -1 to keep going until all issues/prs fetched
# first in each tuple is
pull_rates = [(100, 3), (90, 8), (80, 10), (70, 13), (60, 15), (50, 17), (40, 25), (30, 30), (20, 50), (12, 100)]


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
def run_query(auth, owner, repo, pull_type):  # TODO appending comments
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
    above_threshold = True

    # initial pull rate is (12, 100)
    pr_index = 0

    i = 0
    # query can only fetch at most 100 at a time, so keeps fetching until all fetched
    while has_next_page and above_threshold and i != max_iterations:
        i += 1

        # forms the query and performs call, on subsequent iterations passes in cursor for pagination
        query = get_comments_query(repo, owner, pull_type, pull_rates[pr_index], cursor)
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

            # checks if any of the issues/prs have fewer than threshold comments
            # if so, remove them and stop fetching
            last_count = trimmed_request["edges"][-1]["node"]["comments"]["totalCount"]
            if last_count < comment_threshold:
                above_threshold = False
                for node in reversed(trimmed_request["edges"]):
                    if node["node"]["comments"]["totalCount"] < comment_threshold:
                        trimmed_request["edges"].pop()
                    else:
                        break
            else:
                for j, rate in enumerate(pull_rates):
                    if last_count != 0 and last_count % 100 == 0:
                        pr_index = 0
                        break
                    if (last_count % 100) <= rate[1]:
                        pr_index = j
                        break

            for j, edge in enumerate(trimmed_request["edges"]):
                node = edge["node"]
                node["comments"]["nodes"] = []
                comments = get_comments(node["number"], repo, owner, pull_type[0:-1], headers)

                if len(comments) >= comment_threshold:
                    node["comments"]["nodes"].append(comments)
                    node["comments"]["totalCount"] = len(comments)
                else:
                    trimmed_request["edges"].pop(j)

            json_list.append(trimmed_request["edges"])  # add to final list
            print(f"{i * 100} {pull_type} gathered")

        else:
            print(f"Status code: {str(request.status_code)} on iteration {i}. Retrying")
            i -= 1

    json_string = json.dumps(json_list, indent=4)
    write_to_file(json_string, repo, pull_type)
    # pprint(json_string)
    return json_string


# gets comments for an issue/pr
def get_comments(number, repo, owner, p_type, headers, cursor=None):  # todo try get multiple comments at once

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
            except KeyError:
                print("error while pulling comments")
                break
            # pprint(trimmed_request)

            # determines if all comments have been fetched
            has_next_page = comments["pageInfo"]["hasNextPage"]
            if has_next_page:
                cursor = comments["pageInfo"]["endCursor"]

            filtered_comments = filter_comments(comments["edges"])

            if comment_list is None:
                comment_list = filtered_comments
            else:
                comment_list += filtered_comments
        else:
            print(f"Status code: {str(request.status_code)} while fetching comments. Retrying")

    return comment_list


# filter out any comments made by bots
def filter_comments(comment_list):
    return_list = []
    # iterates through each comment removes it if it was made by a bot
    for comment in comment_list:
        try:
            if comment["node"]["author"]["__typename"] != "Bot":
                return_list.append(comment)
        except TypeError:
            # if account deleted, author will be None so give it login deletedUser
            comment["node"]["author"] = {'login': 'deletedUser'}

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
def get_comments_query(repo, owner, p_type, pull_rate, cursor=None):
    # for pagination
    if cursor is not None:
        start_point = f', after: "{cursor}"'
    else:
        start_point = ""

    query = """
        {
            repository(name: "%s", owner: "%s") {
                %s(first:%d, orderBy:{field: COMMENTS, direction: DESC}%s) {
                    edges {
                        node {
                            number
                            title
                            author {
                                login
                            }
                            state
                            comments(first: %d) {
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
        """ % (repo, owner, p_type, pull_rate[0], start_point, pull_rate[1])

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
