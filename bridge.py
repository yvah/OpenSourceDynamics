import cloudant
from db import DB2
from pr_nlu_analysis import Repository
from query import run_query
import json


def use_existing_data(table):
    db = DB2("db2_credentials.json")
    db.copy_into("SOURCE", table)
    db.close()


def use_new_data(auth, repo, pull_type):
    # database = cloudant.CDatabase("cloudant_credentials.json")
    db = DB2("db2_credentials.json")

    owner_repo = repo.split("/")
    table = f"{owner_repo[0]}_{owner_repo[1]}_{pull_type}"
    add_name(table)

    db.create(table)
    db.clear(table)

    data = run_query(auth, owner_repo[0], owner_repo[1], pull_type)
    repo = Repository(json.loads(data), pull_type)
    db.add_data(table, repo.repo_items)
    # repo.to_csv()
    # repo.stats_to_csv()

    db.copy_into("SOURCE", table)
    db.close()


# adds the name of a database to a file
def add_name(name):
    with open("tables.txt", "r+") as tables:
        if name not in tables.read():
            tables.write(name + "\n")


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

    use_new_data(auth, own_re, p_type)
