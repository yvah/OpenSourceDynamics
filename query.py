from classes import *
from pprint import pprint
from requests import post


def run_query(owner, repo, auth):

    # list to store each comment
    issues = []

    # stores the authorisation token and accept
    headers = {
        "Authorization": "token " + auth,
        "Accept": "application/vnd.github+json",
    }

    # for pagination
    has_next_page = True
    end_cursor = None

    # query can only fetch 100 comments, so keeps fetching until all fetched
    while has_next_page:

        # gets the query and performs call, on subsequent call passes in end_cursor for pagination
        query = get_issue_query(owner, repo, end_cursor)
        print("Gathering issues...")
        request = post('https://api.github.com/graphql', json={'query': query}, headers=headers)

        # if api call was successful, adds the comment to the comment list
        if request.status_code == 200:
            # trims the result of the api call to remove unneeded nesting
            # pprint(request.json())
            trimmed_request = request.json()["data"]["repository"]["issues"]
            # pprint(trimmed_request)

            # determines if all comments have been fetched
            has_next_page = trimmed_request["pageInfo"]["hasNextPage"]
            has_next_page = False  # TODO remove for pagination
            if has_next_page:
                end_cursor = trimmed_request["pageInfo"]["endCursor"]
            for edge in trimmed_request["edges"]:
                issues.append(newIssue(edge["node"]))
        else:
            raise Exception("Query failed to run by returning code of {}.".format(request.status_code))

    return issues


# returns query for issue comments
def get_issue_query(repo, owner, end_cursor=None):

    # for pagination
    if end_cursor is not None:
        after = f', after:"{end_cursor}"'
    else:
        after = ""

    query = """
    {
        repository(name: "%s", owner: "%s") {
            issues(last:100%s) {
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
    """ % (repo, owner, after)

    return query


# main function for testing code
if __name__ == '__main__':
    owner = "flutter"
    repo = "flutter"
    branch = "master"

    print("Enter access token: ", end="")
    auth = input()

    test = run_query(owner, repo, auth)
    pprint(test)
    print(len(test))
