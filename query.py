
from pprint import pprint
from requests import post


def run_query(owner, repo, auth):

    # list to store each comment
    comments = []

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
        request = post('https://api.github.com/graphql', json={'query': query}, headers=headers)
        # trims the result of the api call to remove unneeded nesting
        trimmed_request = request.json()["data"]["repository"]["issueOrPullRequest"]["comments"]
        # pprint(trimmed_request)

        # determines if all comments have been fetched
        has_next_page = trimmed_request["pageInfo"]["hasNextPage"]
        if has_next_page:
            end_cursor = trimmed_request["pageInfo"]["endCursor"]

        # if api call was successful, adds the comment to the comment list
        if request.status_code == 200:
            for edge in trimmed_request["edges"]:
                comments.append(edge["node"])
        else:
            raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

    # todo: store comments in objects

    return comments


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
            issueOrPullRequest(number:120223) {
                ... on Issue {
                    comments(first:100%s) {
                        pageInfo {
                            hasNextPage
                            endCursor
                        }
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
        }
    }
    """ % (owner, repo, after)

    return query


# main function for testing code
if __name__ == '__main__':
    owner = "flutter"
    repo = "flutter"
    branch = "master"
    auth = "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"

    test = run_query(owner, repo, auth)
    pprint(test[0])
