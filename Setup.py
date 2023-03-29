from flask import Flask, render_template, request
from query import run_query
from pr_nlu_analysis import Repository
from time import time
import json
app = Flask(__name__, static_folder="templates", static_url_path="")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/query", methods=["POST"])
def query():
    # input tag in html requires name attribute that will be used in request.form[]
    user = request.form["user"]
    repo = request.form["repo"]
    type = request.form["type"]
    owner_repo = repo.split("/")
    print(user, repo, type)
    data = run_query(user,owner_repo[0],owner_repo[1],type, "w", "name")
    data = json.loads(data)
    print("Performing sentiment analysis...\n")
    start_time = time()
    repo = Repository(data)
    end_time = time()
    print(repo)
    print('\nSentiment analysis took', round(end_time - start_time, 3), 'seconds to run')
    return render_template("index.html")
if __name__ == '__main__':
   app.run()
# use https://raw.githubusercontent.com/yvah/SwEng-group13/API/query.py as source for query
