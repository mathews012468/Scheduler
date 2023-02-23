import datetime
import logging
from classes import Staff, Role, Weekdays
logger = logging.getLogger(__name__)

def staffWorkingToday(roleStaffPairs, weekday):
	scheduledStaff = set()
	for pair in roleStaffPairs:
		if pair[0].day == weekday:
			scheduledStaff.add(pair[1])
	return scheduledStaff


def createSchedule(roleCollection, staffCollection):
    schedule = []
    roleCollection.sort(key= lambda role: len(role.qualifiedStaff))
    for role in roleCollection:
        availableStaff = [staff for staff in staffCollection if staff.isAvailable(role) and staff.isQualified(role)]
        logger.info(f'Available staff for {role.name} on {role.day.name}: {availableStaff}')
        preferedStaff = [staff for staff in availableStaff if role.name in staff.rolePreference]
        if preferedStaff != []:
            availableStaff = preferedStaff
        #staff = selectStaff(availableStaff,schedule, role)
        staff = availableStaff[0]
        schedule.append((role,staff))
    return schedule

def selectStaff(staffPool, schedule, role):
    staffPool.sort(key= lambda staff: staff.shiftsRemaining(schedule), reverse= True)
    for staff in staffPool:
        if staff.isScheduled(role, schedule) == False:
            return staff
        if staff.doubles == True:
            logger.info(f'{staff.name} has doubles as {True}')
            return staff
        else:
            continue
    logger.warning('No staff found')
    return Staff('Unassigned',99)
    

def validatePayload(payload, schema):
    """ Takes in payload and checks key/value pairs against a schema """
    payloadType, schemaType = type(payload), type(schema)
    if payloadType != schemaType:
        raise ValueError(f'payload: {payload} type does not match schema: {schema}')
    
    if schemaType == dict:
        if set(schema.keys()) != set(payload.keys()):
            raise ValueError(f'payload: {payload.keys()} does not match schema: {schema.keys()}')
        for key in schema.keys():
            payloadValue, schemaValue = payload[key], schema[key]
            validatePayload(payloadValue, schemaValue)
    
    if schemaType == list:
        for payloadValue in payload:
            schemaValue = schema[0]
            validatePayload(payloadValue, schemaValue)
    
    return True


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
        jsonObject = {}
        jsonObject['name'] = role.name
        jsonObject['staff'] = staff.name
        jsonObject['day'] = role.day.name
        jsonObject['callTime'] = role.callTime.strftime('%H:%M')
        scheduleJSON.append(jsonObject)
    return scheduleJSON