import cloudant
from db2 import DB2
from pr_nlu_analysis import Repository
from query import run_query


def run_all(auth, repo, pull_type, use_existing):
    # database = cloudant.CDatabase("cloudant_credentials.json")
    db = DB2("db2_credentials.json")

    if pull_type == "pullRequests":
        table = f"{repo}-pull_requests"
    else:
        table = f"{repo}-{pull_type}"

    if not use_existing:
        db.create(table)
        db.clear(table)
        owner_repo = repo.split("/")
        data = run_query(auth, owner_repo[0], owner_repo[1], pull_type, db, table)

        repo = Repository(data)
        db.add_data(table, repo.pull_requests)
        repo.to_csv()
        repo.stats_to_csv()

    db.copy_into("RESULTS", table)


# main function for testing code
if __name__ == '__main__':

    print("Enter an access token: ", end="")
    auth = input()

    p_type = ""
    own_re = ""
    valid = False

    while not valid:
        print("Enter a repo (owner/repo): ", end="")
        own_re = input()
        if len(own_re.split("/")) != 2:
            print("Invalid input")
        else:
            print("Get issues or pull requests? (i or p): ", end="")
            letter = input()

            if letter == "i":
                p_type = "issues"
                valid = True
            elif letter == "p":
                p_type = "pullRequests"
                valid = True
            else:
                print("Invalid input")

    run_all(auth, own_re, p_type, False)
