from flask import Flask, render_template
from flask import request
app = Flask(__name__)
@app.route("/")
def index():
    user = request.form["user"]
    repo = request.form["repo"]
    type = request.form["type"]
    print(user, repo, type)
    return render_template("index.html")
if __name__ == '__main__':
   app.run()
   
# use https://raw.githubusercontent.com/yvah/SwEng-group13/API/query.py as source for query
