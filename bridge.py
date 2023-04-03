import cloudant
from db import DB2
from pr_nlu_analysis import Repository
from query import run_query
import json


# switch source to existing data set
def use_existing_data(table):
    db = DB2("credentials/db2_credentials.json")
    db.switch_view("SOURCE", table)
    db.close()


# gather from new repo and switch source
def use_new_data(auth, repo, pull_type):
    # database = cloudant.CDatabase("credentials/cloudant_credentials.json")

    owner_repo = repo.split("/")
    table = f"{owner_repo[0]}_{owner_repo[1]}_{pull_type}"
    add_name(table)

    # collect data and add it to the database
    data = run_query(auth, owner_repo[0], owner_repo[1], pull_type)
    repo = Repository(data, pull_type)
    # repo.to_csv()
    # repo.stats_to_csv()

    # create connection to DB2
    db = DB2("credentials/db2_credentials.json")
    # create and clear the table in case it doesn't exist or already has data
    db.create(table)
    db.clear(table)
    # insert data into the table
    db.insert_data(table, repo.repo_items)

    # switch the source to the gathered data
    db.switch_view("SOURCE", table)
    db.close()


# adds the name of a database to a file
def add_name(name):
    with open("data/tables.txt", "r+") as tables:
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
