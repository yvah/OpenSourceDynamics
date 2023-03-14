import classes
import json
import query
from requests import post
from pprint import pprint


if __name__ == "__main__":

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


def test_newComment():
    string = """{
        "author": {"login": "Frankie"},
        "bodyText": "this is a comment",
        "createdAt": "2023-02-16T17:20:39Z"
        }"""

    comment1 = classes.newComment(json.loads(string))
    comment2 = classes.Comment("this is a comment", "Frankie", "2023-02-16", "17:20:39")

    assert comment1 == comment2


def test_newIssue():
    string = """{
    "author": {"login": "Fredrick"},
    "comments": {"edges": [{"node": {"author": {"login": "Frankie"},
    "bodyText": "this is a comment",
    "createdAt": "2023-02-16T17:20:39Z"}}]},
    "number": 13,
    "state": "CLOSED",
    "title": "hi"
    }"""

    issue1 = classes.newIssueOrPullRequest(json.loads(string))
    issue2 = classes.IssueOrPullRequest("hi", 13, "CLOSED", "Fredrick",
                                        [classes.Comment("this is a comment", "Frankie", "2023-02-16", "17:20:39")])

    assert issue1 == issue2
