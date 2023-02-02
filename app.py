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
            "qualifiedStaff": [
                str()
            ],
            "day": str()
        }
    ],
    "staff": [
        {
            "name": str(),
            "maxShifts": int(),
            "availability": {
                "MONDAY": [
                    str()
                ],
                "TUESDAY": [
                    str()
                ],
                "WEDNESDAY": [
                    str()
                ],
                "THURSDAY": [
                    str()
                ],
                "FRIDAY": [
                    str()
                ],
                "SATURDAY": [
                    str()
                ],
                "SUNDAY": [
                    str()
                ]
            },
            "rolePreference": [
                str()
            ],
            "doubles": bool()
        }
    ]
}

app = Flask(__name__)
app.config['roleStaffSchema'] = schema #TODO: config from seperate file

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
    return schedule

@app.route('/input', methods=['POST'])
def validateResponse():
    requestData = request.get_json()
    if requestData == None:
        return 'Alert: Check payload header'
    isValid = validatePayload(requestData, app.config["roleStaffSchema"])
    if not isValid:
        return {"error": 'not valid input'}, 400
    roleCollection = [parseRole(role) for role in requestData['roles']]
    staffCollection = [parseStaff(staff) for staff in requestData['staff']]

    schedule = main.createSchedule(roleCollection, staffCollection)

    scheduleAsJson = scheduleToJSON(schedule)
    
    return scheduleAsJson

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

def printWeekSchedule(schedule):
	for day in Weekdays:
		print(day.name)
		dayPairs = [pair for pair in schedule if pair[0].day == day]
		for pair in dayPairs:
			print(pair[0].name, pair[1].name)
    
#if dict, check that keys are the same and schema of values are the same
#if list, check that schema of values are the same
#if plain value, check that type is the same
def validatePayload(payload, schema):
    """ Takes in payload and checks key/value pairs against a schema """
    payloadType, schemaType = type(payload), type(schema)
    if payloadType != schemaType:
        return False
    
    isValid = True
    if schemaType == dict:
        if list(schema.keys()) != list(payload.keys()):
            return False
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