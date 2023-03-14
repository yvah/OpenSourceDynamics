import query
from requests import post
from pprint import pprint


def test1():
    print("Enter an access token: ", end="")
    auth = input()

    headers = {
        "Authorization": "token " + auth,
        "Accept": "application/vnd.github+json",
    }

    preliminary_query = """
    {
        repository(name: "flutter", owner: "flutter") {
            issue(number: 1831) {
                comments(first:100) {
                    edges {
                        node {
                            author {
                                login
                                canReceiveOrganizationEmailsWhenNotificationsRestricted
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
    }
    """

    request = post("https://api.github.com/graphql", json={"query": preliminary_query}, headers=headers)
    trimmed_request = request.json()["data"]["repository"]["issue"]["comments"]

    trimmed_request["edges"] += query.get_other_comments(1831, trimmed_request["pageInfo"]["endCursor"],
                                                         "flutter", "flutter", "issue", headers)

    pprint(trimmed_request)
    print(len(trimmed_request["edges"]))


def test2():
    print("Enter an access token: ", end="")
    auth = input()

    headers = {
        "Authorization": "token " + auth,
        "Accept": "application/vnd.github+json",
    }

    query = """
    {
        repository(name: "chromium", owner: "chromium") {
            pullRequest(number: 134) {
                comments(first:100) {
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
    }
    """

    request = post("https://api.github.com/graphql", json={"query": query}, headers=headers)
    pprint(request.json())
    trimmed_request = request.json()["data"]["repository"]["pullRequest"]

    pprint(trimmed_request)


if __name__ == "__main__":
    print("Which test do you want to run?")
    ans = input()
    if ans == "1":
        test1()
    elif ans == "2":
        test2()
    else:
        print("no test with that number")
