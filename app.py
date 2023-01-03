from flask import Flask
from flask import request
from flask import url_for
from flask import render_template

import nonsense


app = Flask(__name__)

@app.route("/")
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

@app.route('/profile/<username>')
def profile(username):
    return f'{username}\'s profile'

@app.get('/login')
def login_get():
    return 'get log in form'

@app.post('/login')
def login_post():
    return 'post log in'

@app.route('/hello/')
@app.route('/hello/<name>')
def template(name=None):
    return render_template('hello.html', name=name)

with app.test_request_context():
    print(url_for('html'))
    print(url_for('directory'))
    #print(url_for('login'))
    print(url_for('profile', username='TBody'))