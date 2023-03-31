import cloudant
from pr_nlu_analysis import Repository
from query import run_query
import json

def run_all(auth, repo, pull_type):
    database = cloudant.Database("credentials.json")
    if pull_type == "pullRequests":
        database_name = f"{repo}-pull_requests"
    else:
        database_name = f"{repo}-{pull_type}"

    if database.checkDatabases(database_name):
        database.clearDatabase(database_name)
    owner_repo = repo.split("/")
    data = run_query(auth, owner_repo[0], owner_repo[1], pull_type, database, database_name)
    repo = Repository(json.loads(data))
    repo.to_csv()
    repo.stats_to_csv()
