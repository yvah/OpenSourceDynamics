from flask import Flask, render_template

app = Flask(__name__, static_folder="assets", static_url_path="")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/some-pie.html")
def pie():
    return render_template("some-pie.html")


if __name__ == "__main__":
    app.run()