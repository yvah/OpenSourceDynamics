import cloudant
from pr_nlu_analysis import Repository
from query import run_query


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
    repo = Repository(data)
    repo.to_csv()
    repo.stats_to_csv()


# main function for testing code
if __name__ == '__main__':

    print("Enter an access token: ", end="")
    auth = input()

    pull_type = ""
    valid = False

    while not valid:
        print("Enter a repo (owner/repo): ", end="")
        owner_repo = input()
        if len(owner_repo.split("/")) != 2:
            print("Invalid input")
        else:
            print("Get issues or pull requests? (i or p): ", end="")
            letter = input()

            if letter == "i":
                pull_type = "issues"
                valid = True
            elif letter == "p":
                pull_type = "pullRequests"
                valid = True
            else:
                print("Invalid input")

    run_all(auth, owner_repo, pull_type)
