from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__, static_folder="templates", static_url_path="")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/validate", methods=["POST"])
def query():
    # input tag in html requires name attribute that will be used in request.form[]
    user = request.form["user"]
    repo = request.form["repo"]
    type = request.form["type"] # value in tags are 'issues' or 'pull-requests'
    
    if (True):
        return redirect(url_for('results', user = user, repo = repo, type = type))
    else:
        print(user, repo, type)
        return redirect(url_for('index'))
        

@app.route("/<type>/<user>/<repo>")
def results(type, user, repo):
    print(user, repo, type)
    # re check for valid, if someone randomly 
    return render_template("chart.html")

# use https://raw.githubusercontent.com/yvah/SwEng-group13/API/query.py as source for query 

# @app.route("/404")
# def error ():
#     return render_template("404.html")

# @app.route("/blank")
# def blank ():
#     return render_template("blank.html")

# @app.route("/button")
# def Button ():
#     return render_template("button.html")

# @app.route("/chart")
# def chart ():
#     return render_template("chart.html")

# @app.route("/element")
# def Element ():
#     return render_template("element.html")

# @app.route("/form")
# def form ():
#     return render_template("form.html")

# @app.route("/form", methods=["POST", "GET"])
# def retrieve():
#     # print(request.get_data(as_text=True))
#     return render_template("chart.html")

# @app.route("/charts", methods=["POST"])
# def charts ():
#     print(request.form["gridRadios"])
#     return render_template("chart.html")

# @app.route("/signin")
# def signin ():
#     return render_template("signin.html")

# @app.route("/signup")
# def signup ():
#     return render_template("signup.html")

# @app.route("/table")
# def table ():
#     return render_template("table.html")

# @app.route("/typography")
# def typography ():
#     return render_template("typography.html")

# @app.route("/widget")
# def widget ():
#     return render_template("widget.html")

if __name__ == "__main__":
    app.run(debug = True)