from flask import Flask
from flask import request
from flask import url_for
from flask import render_template

from classes import Staff, Role
import json

app = Flask(__name__)

#attempt to understand how a login could function...
def valid_login(userDict, passDict):
    pass

@app.route('/')
def traditions():
    return 'hello world'

@app.route('/JSON', methods = ['GET', 'POST'])
def receiveData(roleStaffData):
    return roleStaffData

    staffList = []
    roleStaffObjects = json.load(roleStaffData)
    for staff in roleStaffObjects['staff']:
        staffObj = Staff(name= staff['name'], maxShifts= staff['maxShifts'], rolePreference= staff['rolePreference'], doubles= staff['doubles'])
        
    

@app.route('/login', methods=['POST','GET'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'],
                       request.form['password']):
            return f"logged in {request.form['username']}"
        else:
            error = 'Invalid username/password'
    return render_template('login.html', error=error)
        

@app.route('/availability/<staff>')
def availability(staff):
    return f'set {staff} availability'


@app.route('/createSchedule')
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