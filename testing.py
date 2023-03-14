import classes
import json


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
