from flask import Flask
from flask import request
import nonsense


app = Flask(__name__)

@app.route("/") #ah, so this is root of the url
def hello():
    name = request.args.get("name")
    preferredRole = request.args.get("role")
    return nonsense.nonsense(name=name, role=preferredRole)

@app.route("/message")
def html():
    return 'some html text'

@app.route("/dir/")
def directory():
    return 'directory?'
