from flask import Flask
from flask import request
import main
import datetime

from classes import Staff, Role, Weekdays

#TODO: config from seperate file

app = Flask(__name__)
app.config.from_object('config.DefaultConfig')
#app.config['roleStaffSchema'] = schema
#I'd like to follow the documentation for seperating the config settings:
# https://flask.palletsprojects.com/en/2.2.x/config/

#However, I don't really understand it
#app.config.from_envvar('KIKISCHEDULER_SETTINGS')
#app.config.from_pyfile('yourconfig.cfg')


@app.route('/')
def traditions():
    return 'hello world'

#if dict, check that keys are the same and schema of values are the same
#if list, check that schema of values are the same
#if plain value, check that type is the same
def validatePayload(payload, schema):
    """ Takes in payload and checks key/value pairs against a schema """
    payloadType, schemaType = type(payload), type(schema)
    if payloadType != schemaType:
        raise ValueError(f'payload: {payload} type does not match schema: {schema}')
    
    isValid = True
    if schemaType == dict:
        if list(schema.keys()) != list(payload.keys()):
            raise ValueError(f'payload: {payload.keys()} does not match schema: {schema.keys()}')
        for key in schema.keys():
            payloadValue, schemaValue = payload[key], schema[key]
            isValueValid = validatePayload(payloadValue, schemaValue)
            isValid = isValid and isValueValid
    
    if schemaType == list:
        for payloadValue in payload:
            schemaValue = schema[0]
            isValueValid = validatePayload(payloadValue, schemaValue)
            isValid = isValid and isValueValid
    
    return isValid


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
        day = role["day"]
        weekday = Weekdays[day]
    except KeyError:
        raise ValueError(f"Day: {day} for Role: {name} not in valid format.")
    return Role(name=name, day=weekday, callTime=callTime, qualifiedStaff=qualifiedStaff)


def parseStaff(staff):
    name = staff["name"]
    maxShifts = staff["maxShifts"]
    try:
        availability = formatAvailability(staff["availability"])
    except ValueError:
        raise ValueError(f"Invalid format for Staff: {name} availability.")
    rolePreference = staff["rolePreference"]
    doubles = staff["doubles"]
    return Staff(name=name, maxShifts=maxShifts, availability=availability, rolePreference=rolePreference, doubles=doubles)


def formatAvailability(availability):
    staffAvailability = {}
    for day, callTimes in availability.items():
        weekday = Weekdays[day]
        weekdayCalltimes = [] #There's something here about creating a new empty list, when 'callTimes' is already a list that feels off...
        for callTime in callTimes:
            hour, minutes = callTime.split(':')
            hour = int(hour)
            minutes = int(minutes[0:2])
            if hour < 12 and 'PM' in callTime:
                hour += 12
            callTime = datetime.time(hour,minutes)
            weekdayCalltimes.append(callTime)
        staffAvailability[weekday] = weekdayCalltimes
    return staffAvailability


def scheduleToJSON(schedule):
    scheduleJSON = []
    for pair in schedule:
        role = pair[0]
        staff = pair[1]
        role.qualifiedStaff = [] # size down the character count for testing.
        role.staff = staff.name
        scheduleJSON.append(role.toJSON())
    
    for obj in scheduleJSON: #this does not seem to work here.
        obj.replace('\\"','') #while it works in the python interpreter to clean the dumped escape characters

    return scheduleJSON


@app.route('/schedule', methods=["POST"])
def createSchedule():
    roleStaffData = request.get_json()
    roleStaffSchema = app.config["SCHEMA"]
    if roleStaffData == None:
        return 'Alert: Check payload header'
    try:
        isValid = validatePayload(roleStaffData,roleStaffSchema)
    except ValueError as err:
        return (err.message) #TODO: return as JSON

    roleCollection = [parseRole(role) for role in roleStaffData["roles"]]
    staffCollection = [parseStaff(staff) for staff in roleStaffData["staff"]]

    schedule = main.createSchedule(roleCollection, staffCollection)
    scheduleJSON = scheduleToJSON(schedule)

    return scheduleJSON