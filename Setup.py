from flask import Flask, render_template, request

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
    print(user, repo, type)
    return render_template("index.html")
if __name__ == '__main__':
   app.run()
# use https://raw.githubusercontent.com/yvah/SwEng-group13/API/query.py as source for query
