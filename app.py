from flask import Flask
from flask import request
from flask import render_template
import main
import datetime

from classes import Staff, Role, Weekdays
import json

#TODO: format availability from incoming json

schema = {
    "roles": [
        {
            "name": str(),
            "callTime": str(),
            "qualifiedStaff": list(),
            "day": str()
        }
    ],
    "staff": [
        {
            "name": str(),
            "maxShifts": int(),
            "availability": dict(),
            "rolePreference": list(),
            "doubles": bool()
        }
    ]
}

app = Flask(__name__)
app.config['activeSchema'] = schema #TODO: config from seperate file

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
    requestData = request.get_json()

    #It's like .get() without .get()
    language = None
    framework = None
    pythonVersion = None
    example = None
    booleanTest = None

    if requestData:
        if 'language' in requestData:
            language = requestData['language']
        if 'framework' in requestData:
            framework = requestData['framework']
        if 'version_info' in requestData:
            pythonVersion = requestData['version_info']['python']
        if 'examples' in requestData:
            example = requestData['examples'][0]
        if 'boolean_test' in requestData:
            booleanTest = requestData['boolean_test']

    return f'''
    The language value is: {language}
    The framework value is: {framework}
    The Python version is: {pythonVersion}
    The item at index 0 of "examples" is: {example}
    The boolean test value is: {booleanTest}
    '''

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

def getAllCallTimes(roles):
    """
    List of Role objects
    """
    dayAndCallTimes = {(role.day, role.callTime) for role in roles}
    callTimes = {weekday: [] for weekday in Weekdays}
    for dayCallTime in dayAndCallTimes:
        weekday = dayCallTime[0]
        callTime = dayCallTime[1]
        callTimes[weekday].append(callTime)
    return callTimes

def parseRole(role):
    """
    Takes in role as dictionary from google sheets app script
    Returns Role object
    """
    name = role["name"]
    try:
        hour, minutes = role["callTime"].split(":")
        hour, minutes = int(hour), int(minutes)
        callTime = datetime.time(hour=hour, minute=minutes)
    except ValueError:
        raise ValueError(f"Call time {role['callTime']} not in a valid format")
    qualifiedStaff = role["qualifiedStaff"]
    try:
        day = role["day"].upper().strip()
        weekday = Weekdays[day]
    except KeyError:
        raise ValueError(f"Role {name} does not have a valid weekday. Weekday passed was {day}.")

    return Role(name=name, day=weekday, callTime=callTime, qualifiedStaff=qualifiedStaff)

def parseStaff(staff):
    name = staff["name"]
    maxShifts = staff["maxShifts"]
    availability = staff["availability"]
    rolePreference = staff["rolePreference"]
    doubles = staff["doubles"]
    return Staff(name=name, maxShifts=maxShifts, availability=availability, rolePreference=rolePreference, doubles=doubles)

@app.route('/schedule', methods=["POST"])
def compileStaff():
    requestData = request.get_json()
    if requestData == None:
        return 'Alert: Check payload header'
    validatePayload(requestData)
    roleCollection = (parseRole(role) for role in requestData["roles"])

    #TODO: defaultAvail = getAllCallTimes(roles)
    staffCollection = [parseStaff(staff) for staff in requestData["staff"]]

    schedule = main.createSchedule(roleCollection, staffCollection)
    print(schedule)
    return schedule

def validatePayload(payload):
    """ Takes in payload and checks key/value pairs against a schema """
    schema = app.config['activeSchema']
    roleCollection, staffCollection = payload.keys()
    
    for role in payload[roleCollection]:
        for (schemaKey, schemaValue), (roleKey, roleValue) in zip(schema[roleCollection][0].items(), role.items(), strict=True):
            assert schemaKey == roleKey
            assert type(schemaValue) == type(roleValue)
    for staff in payload[staffCollection]:
        for (schemaKey, schemaValue), (staffKey, staffValue) in zip(schema[staffCollection][0].items(), staff.items(), strict=True):
            assert schemaKey == staffKey
            assert type(schemaValue) == type(staffValue)