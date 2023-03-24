from flask import Flask, render_template, request

app = Flask(__name__, static_folder="templates", static_url_path="")

@app.route("/")
def index():
    return render_template("index.html")

# use https://raw.githubusercontent.com/yvah/SwEng-group13/API/query.py as source for query

@app.route("/404")
def error ():
    return render_template("404.html")

@app.route("/blank")
def blank ():
    return render_template("blank.html")

@app.route("/button")
def Button ():
    return render_template("button.html")

@app.route("/chart")
def chart ():
    return render_template("chart.html")

@app.route("/element")
def Element ():
    return render_template("element.html")

# @app.route("/form")
# def form ():
#     return render_template("form.html")

@app.route("/form", methods=["RETRIEVE"])
def retrieve():
    owner = request.data["owner"]
    repo = request.data["repo"]
    source = request.form.get("gridRadios")
    print(owner, repo, source, file='sys.stdout')
    # if issues
        # run_query(auth, owner, repo, pull_type)
    return render_template("form.html")

@app.route("/signin")
def signin ():
    return render_template("signin.html")

@app.route("/signup")
def signup ():
    return render_template("signup.html")

@app.route("/table")
def table ():
    return render_template("table.html")

@app.route("/typography")
def typography ():
    return render_template("typography.html")

@app.route("/widget")
def widget ():
    return render_template("widget.html")

if __name__ == "__main__":
    app.run(debug = True)