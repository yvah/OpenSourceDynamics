from flask import Flask, render_template, request
from bridge import run_all
from pr_nlu_analysis import Repository
from time import time
import numpy
import json
import webbrowser
app = Flask(__name__, static_folder="templates, fetched_data", static_url_path="")

@app.route("/", methods=["GET"])
def index():
    pre_pulled = numpy.array(["Flutter", "swEng", "Microsoft Windows"])
    return render_template("index.html", pre_pulled=pre_pulled)

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

@app.route("/pulled", methods=["POST"])
def pulled():
    repo = request.form["Pre-Pulled Data"]
    print(repo)
    
    return webbrowser.open("https://eu-gb.dataplatform.cloud.ibm.com/dashboards/76dcd7cf-ca85-4654-b47a-02610eac5955/view/5f65e53600b009ea6de3c4e40799280374312255b0bb8a01d6837b4909642297a86a4093c87c1e08d9175363f5b91a5acd")
if __name__ == '__main__':
   app.run()
# use https://raw.githubusercontent.com/yvah/SwEng-group13/API/query.py as source for query
