from flask import Flask, render_template, request
from bridge import run_all
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
    #owner_repo = repo.split("/")
    print(user,repo,type)
    run_all(user,repo,type)
    return render_template("index.html")
if __name__ == '__main__':
   app.run()
# use https://raw.githubusercontent.com/yvah/SwEng-group13/API/query.py as source for query
