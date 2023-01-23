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

@app.route('/query_example')
def query_example():
    language = request.args.get('language')
    framework = request.args.get('framework')
    website = request.args.get('website')

    return f"""
    <h1>The language value is: {language}</h1>
    <p>The framework value is: {framework}</p>
    The website value is: {website}
    """

@app.route('/form_example', methods=['GET','POST'])
def form_example():
    if request.method == 'POST':
        language = request.form.get('language')
        framework = request.form.get('framework')
        return f'''
        <p>The language value is: {language}</p>
        The framework value is: {framework}'''
    #else handle the 'GET' request
    #return html to display a form which POSTS on submit
    return """
    <form method='POST'>
    <div><label>Langue: <input type='text' name='language'></label</div>
    <div><label>Framework: <input type'text' name='framework'</label></div>
    <input type='submit' value='Submit'>
    </form>"""


@app.route('/json_example', methods=['POST'])
def json_example():
    return 'JSON Object Example'


@app.route('/')
def traditions():
    return 'hello world'

        
@app.route('/availability/<staff>')
def availability(staff):
    return f'set {staff} availability'


@app.route('/hello/')
@app.route('/hello/<name>')
def template(name=None):
    return render_template('hello.html', name=name)