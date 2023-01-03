from flask import Flask
from flask import request
from flask import url_for
from flask import render_template

import nonsense
import main

#Staff and role objects 'pre-processed?' 


app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return 'log in form'
    if request.method == 'POST':
        return 'do log in'

@app.route('/availability/<staff>')
def availability(staff):
    return f'set {staff} availability'

app.route('/createSchedule')
def createSchedule():
    return f'create schedule'

@app.route("/showsense")
def sense():
    name = request.args.get("name")
    preferredRole = request.args.get("role")
    return nonsense.nonsense(name=name, role=preferredRole)

@app.route('/profile/<username>')
def profile(username):
    return f'{username}\'s profile'

@app.route('/hello/')
@app.route('/hello/<name>')
def template(name=None):
    return render_template('hello.html', name=name)

with app.test_request_context():
    print(url_for('login'))
    print(url_for('availability', staff='TBody'))