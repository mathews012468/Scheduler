import random, datetime
from enum import Enum

class Weekday(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

class Role:
    def __init__(self, name, day, callTime=None ):
        self.name = name
        self.day = day

        #default callTimes based on name
        callTimes = {
        'lunch': datetime.time(hour=10, minute=30),
        'brunch': datetime.time(hour=10, minute=30),
        'brunchdoor': datetime.time(hour=12, minute=00),
        'swing': datetime.time(hour=13),
        'FMN': datetime.time(hour=14),
        'shermans': datetime.time(hour=16, minute=30),
        'veranda': datetime.time(hour=16, minute=30),
        'outside': datetime.time(hour=16, minute=30),
        'bbar': datetime.time(hour=16, minute=30),
        'vbar': datetime.time(hour=16, minute=30),
        'front': datetime.time(hour=16, minute=30),
        'uber': datetime.time(hour=16, minute=30),
        'door': datetime.time(hour=18),
        'back': datetime.time(hour=18),
        'middle': datetime.time(hour=18),
        'shermans6pm': datetime.time(hour=18),
        'aux': datetime.time(hour=18)
        }
        self.callTime = callTimes.get(name)


class Staff:
    def __init__(self, name, maxShifts, availability):
        self.name = name
        self.maxShifts = maxShifts
        self.availability = availability

def createRoles(compiledRoles): #Question: move this function to test_code.py?
    """Create Role Objects from compiled roles.txt input
    Input: List of dictionaries from testing_code.compileWeek()
    Output: A list of lists containing Role Objects for each weekday
    """
    rolesOfWeek = []
    for dict in compiledRoles:
        for weekday,roles in dict.items():
            rolesOfDay = [Role(name=roleName, day=weekday) for roleName in roles]
        rolesOfWeek.append(rolesOfDay)
    return rolesOfWeek


def isAvailable(role, staff):
    """check if role.callTime is in staff.availability"""
    day = role.day
    staffAvail = staff.availability[day]
    for i in range(0, len(staffAvail), 2): # iterate over staffAvail in 'chunks' of 2.
        availPair = staffAvail[i:i+2]
        startTime = availPair[0]
        endTime = availPair[1]
        if role.callTime >= startTime and role.callTime <= endTime:
            return True
        else:
            continue
    return False


def createWeekSchedule(rolesOfWeek, staffList):
    """Pair a member of staff with each role in a weekday of Roles
    input: list of Role objects from createRoles() and a list of Staff Objects
    output: a list of lists containing tuples of (RoleObject, StaffObject) pairs for each weekday
    """
    global weekSchedule # global for other functions to access.
    weekSchedule = []
    for day in rolesOfWeek:
        daySchedule = []
        for role in day:
            availableStaff = [staff for staff in staffList if isAvailable(role, staff)]
            roleStaffPair = (role, random.choice(availableStaff))
            daySchedule.append(roleStaffPair)
        weekSchedule.append(daySchedule)
    return weekSchedule


def scheduleView(schedule):
    """print schedule to screen"""
    for day in schedule:
        headerDate = day[0][0].day #day of first Role object
        print(f'---{headerDate}---')
        for roleStaffPair in day:
            role = roleStaffPair[0]
            staff = roleStaffPair[1]
            print(f'{role.name}: {staff.name}')

