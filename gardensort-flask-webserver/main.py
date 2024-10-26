from flask import Flask, render_template, url_for, request
from markupsafe import escape






app = Flask(__name__)

@app.route('/')
def index_load():
    return render_template("index.html")

if __name__ == '__main__':
    app.run("localhost", "3022", debug=True, use_reloader=False)