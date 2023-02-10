from apps import create_app
from flask import render_template

app = create_app()

@app.route("/")
def home():
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)