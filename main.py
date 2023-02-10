import datetime
from classes import Staff, Role, Weekdays


# main is sparse and clean.
# All the indecision has been shoved under the rug of testingCode.

def staffWorkingToday(roleStaffPairs, weekday):
	scheduledStaff = set()
	for pair in roleStaffPairs:
		if pair[0].day == weekday:
			scheduledStaff.add(pair[1])
	return scheduledStaff


def createSchedule(roleCollection, staffCollection):
	"""
	returns a 'schedule as a list of (role,staff) pair tuples
	Assumes Role and Staff objects have been compiled from spreadsheet database
	"""
	roleCollection.sort(key=lambda role: len(role.qualifiedStaff))
	roleStaffPairs = []
	for role in roleCollection:
		availableStaff = [staff for staff in staffCollection if staff.name in role.qualifiedStaff and staff.isAvailable(role) and staff not in staffWorkingToday(roleStaffPairs, role.day)] # I don't like how long this line is.
		#availableStaff = [staff for staff in availableStaff if role.name in staff.rolePreference]
		availableStaff = [staff for staff in availableStaff if staff.shiftsRemaining(roleStaffPairs) > 0]
		if availableStaff == []:
			unassigned = Staff(name='Unassigned',maxShifts=None, availability=None)
			roleStaffPairs.append((role,unassigned))
			continue
		availableStaff.sort(key = lambda staff: staff.shiftsRemaining(roleStaffPairs), reverse=True)
		staff = availableStaff[0]
		roleStaffPairs.append((role,staff))
	return roleStaffPairs


def validatePayload(payload, schema):
    """ Takes in payload and checks key/value pairs against a schema """
    payloadType, schemaType = type(payload), type(schema)
    if payloadType != schemaType:
        raise ValueError(f'payload: {payload} type does not match schema: {schema}')
    
    if schemaType == dict:
        if list(schema.keys()) != list(payload.keys()):
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