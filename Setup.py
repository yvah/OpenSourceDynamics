from flask import Flask, render_template, request
from bridge import use_existing_data, use_new_data
from time import time
import json
import webbrowser
app = Flask(__name__, static_folder="templates", static_url_path="")


@app.route("/", methods=["GET"])
def index():
    with open(r"data/tables.txt", 'r') as fp:
        lines = fp.readlines()
        pre_pulled = []
        for row in lines:
             pre_pulled.append(row)
             
    print(pre_pulled)
    return render_template("index.html", pre_pulled=pre_pulled)


@app.route("/query", methods=["POST"])
def query():
    # input tag in html requires name attribute that will be used in request.form[]
    user = request.form["user"]
    repo = request.form["repo"]
    p_type = request.form["type"]
    # owner_repo = repo.split("/")
    print(user, repo, p_type)
    use_new_data(user, repo, p_type)
    return render_template("dashboard.html")


@app.route("/pulled", methods=["POST"])
def pulled():
    repo = request.form["Pre-pulled Data"]
    use_existing_data(repo)
    
    return render_template("dashboard.html")


if __name__ == '__main__':
    app.run()
# use https://raw.githubusercontent.com/yvah/SwEng-group13/API/query.py as source for query
