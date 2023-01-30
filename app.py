from flask import Flask
from flask import request
import main
import datetime

from classes import Staff, Role, Weekdays

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

@app.route('/')
def traditions():
    return 'hello world'

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