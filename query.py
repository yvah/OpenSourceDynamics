from classes import newIssueOrPullRequest
from pprint import pprint
from requests import post


def run_query(auth, owner, repo, type):

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
        query = get_issue_query(owner, repo, type, end_cursor)
        print("Gathering issues...")
        request = post('https://api.github.com/graphql', json={'query': query}, headers=headers)

        # if api call was successful, adds the comment to the comment list
        if request.status_code == 200:
            # trims the result of the api call to remove unneeded nesting
            # pprint(request.json())
            try:
                trimmed_request = request.json()["data"]["repository"][type]
            except TypeError:
                print("Invalid information provided")
                break
            # pprint(trimmed_request)

            # determines if all comments have been fetched
            has_next_page = trimmed_request["pageInfo"]["hasNextPage"]
            has_next_page = False  # TODO remove for pagination
            if has_next_page:
                end_cursor = trimmed_request["pageInfo"]["endCursor"]
            for edge in trimmed_request["edges"]:
                issues.append(newIssueOrPullRequest(edge["node"]))
        else:
            print("Invalid information provided")
            break

    return issues


# returns query for issue comments
def get_issue_query(repo, owner, type, end_cursor=None):

    # for pagination
    if end_cursor is not None:
        after = f', after:"{end_cursor}"'
    else:
        after = ""

    query = """
    {
        repository(name: "%s", owner: "%s") {
            %s(last:100%s) {
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
    """ % (repo, owner, type, after)

    return query


# main function for testing code
if __name__ == '__main__':

    valid = True

    print("Enter an access token: ", end="")
    auth = input()
    print("Enter a repo (owner/repo): ", end="")
    temp = input()
    owner_repo = temp.split("/")
    if len(owner_repo) != 2:
        print("Invalid input")
        valid = False
    else:
        print("Get issues or pull requests? (i or p): ", end="")
        letter = input()

        if letter == "i":
            pull_type = "issues"
        elif letter == "p":
            pull_type = "pullRequests"
        else:
            print("Invalid input")
            valid = False

    if valid:
        test = run_query(auth, owner_repo[1], owner_repo[0], pull_type)
        if test:
            pprint(test)
