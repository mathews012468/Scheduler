from flask import Flask
from flask import request
import nonsense


app = Flask(__name__)

@app.route("/")
def hello():
    name = request.args.get("name")
    preferredRole = request.args.get("role")
    return nonsense.nonsense(name=name, role=preferredRole)