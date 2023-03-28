import cloudant
from pull_request_comment_analysis import Repository
from query import run_query


def run_all(auth, repo, owner, pull_type):

    database = cloudant.Database("credentials.json")
    if pull_type == "pullRequests":
        database_name = f"{owner}/{repo}-pull_requests"
    else:
        database_name = f"{owner}/{repo}-{pull_type}"

    if database.checkDatabases(database_name):
        database.clearDatabase(database_name)

    data = run_query(auth, owner, repo, pull_type, database, database_name)
    repo = Repository(data)
    print(repo)
