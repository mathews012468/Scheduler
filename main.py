import datetime
import logging
import random
from classes import Staff, Role, Weekdays
logger = logging.getLogger(__name__)

def staffWorkingToday(roleStaffPairs, weekday):
	scheduledStaff = set()
	for pair in roleStaffPairs:
		if pair[0].day == weekday:
			scheduledStaff.add(pair[1])
	return scheduledStaff

def getPossibleStaff(role, staffCollection):
    availableStaff = [staff for staff in staffCollection if staff.isAvailable(role)]
    if availableStaff == []:
        logger.warning(f'no available staff for {role}')
    logger.info(f'available staff for {role}:\n{availableStaff}')
    qualifiedStaff = [staff for staff in staffCollection if staff.isQualified(role)]
    if qualifiedStaff == []:
        logger.warning(f'no qualified staff for {role}')
    logger.info(f'qualified staff for {role}:\n{qualifiedStaff}')

    #TODO: move list of schedule restrictions (filters?) to another place and pass the list these functions.
    possibleStaff = [staff for staff in availableStaff and qualifiedStaff]
    logger.info(f'possible staff for {role}:\n{possibleStaff}')
    return possibleStaff

def getStaffPool(role, possibleStaff, schedule):
    noDoubles = [
    staff for staff in possibleStaff if
    staff.isScheduled(role, schedule) == False
    or
    staff.isScheduled(role, schedule) == True and staff.doubles == True
    ]
    if noDoubles == []:
        logger.warning(f'no staff without a double for {role}')
    logger.info(f'staff without a double for {role}:\n{noDoubles}')
    shiftsRemaining = [staff for staff in possibleStaff if staff.shiftsRemaining(schedule) > 0]
    if shiftsRemaining == []:
        logger.warning(f'no staff with shifts remaining for {role}')
    logger.info(f'staff with shifts remaining for {role}:\n{shiftsRemaining}')

    staffPool = [staff for staff in noDoubles and shiftsRemaining]
    logger.info(f'staff pool for {role}:')
    if staffPool == []:
        logger.warning(f'staff pool empty- opening restrictions')
        staffPool = [staff for staff in noDoubles]

    for staff in staffPool:
        logger.info(f'{staff}, {staff.shiftsRemaining(schedule)}')
    return staffPool

def selectStaff(role, staffPool, schedule):
    if staffPool == []:
        unassigned = Staff('Unassigned',99)
        logger.error(f'{role} paired with Unassigned Staff')
        return unassigned

    preferredStaff = [staff for staff in staffPool if staff.name in role.preferredStaff]
    if preferredStaff == []:
        logger.warning(f'no prefered staff available')
    if preferredStaff != []:
        logger.info(f'selecting from preferred staff')
        staffPool = preferredStaff
    staffPool.sort(key= lambda staff: staff.shiftsRemaining(schedule), reverse= True)
    staff = staffPool[0]
    logger.info(f'selected staff for {role}: {staff}')
    return staff

def createSchedule(roleCollection, staffCollection):
    schedule = []
    roleCollection = random.sample(roleCollection, k=len(roleCollection))
    roleCollection.sort(key= lambda role: len(role.preferredStaff), reverse= True)
    for role in roleCollection:
        possibleStaff = getPossibleStaff(role, staffCollection)
        staffPool = getStaffPool(role, possibleStaff, schedule)
        staff = selectStaff(role, staffPool, schedule)
        schedule.append((role,staff))
    return schedule
    

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
    preferredStaff = role["preferredStaff"]
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