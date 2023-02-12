from dataclasses import dataclass


@dataclass
class Comment:
    body: str
    author: str
    date: str
    time: str


def newComment(raw):
    body = raw["bodyText"]
    author = raw["author"]["login"]
    date_time = raw["createdAt"]

    date = date_time[0:10]
    time = date_time[11:19]

    return Comment(body, author, date, time)

