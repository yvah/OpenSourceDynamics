from dataclasses import dataclass


@dataclass
class IssueOrPullRequest:
    title: str
    number: int
    state: str
    author: str
    comments: []


def newIssueOrPullRequest(raw):
    title = raw["title"]
    number = raw["number"]
    state = raw["state"]
    author = raw["author"]["login"]
    comments = []

    for edge in raw["comments"]["edges"]:
        comments.append(newComment(edge["node"]))

    return IssueOrPullRequest(title,number,state,author,comments)


@dataclass
class Comment:
    body: str
    author: str
    date: str
    time: str


def newComment(raw):
    body = raw["bodyText"]
    author = raw["author"]["login"]     # TODO fix NoneType error
    date_time = raw["createdAt"]

    date = date_time[0:10]
    time = date_time[11:19]

    return Comment(body, author, date, time)



