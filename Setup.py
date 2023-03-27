from flask import Flask, render_template

app = Flask(__name__)
@app.route("/")
def index():
    return render_template("index.html")
if __name__ == '__main__':
   app.run()
# use https://raw.githubusercontent.com/yvah/SwEng-group13/API/query.py as source for query
