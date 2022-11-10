import random, datetime
from enum import Enum

class Weekday(Enum):
    MONDAY = 0
    TUESDAY = 1
    WENDESDAY = 2
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
        'lunch': 10.30, #Question: Use datetime.time instead of int?
        'front': 16.30,
        'aux': 18.00
        }
        self.callTime = callTimes.get(name)


class Staff:
    def __init__(self, name, availability=None):
        self.name = name
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


def createWeekSchedule(rolesOfWeek, staffList): #TODO: create list of Staff Objects from input.
    """Pair a member of staff with each role in a weekday of Roles
    input: list of Role objects from createRoles() and a list of Staff Objects
    output: a list of lists containing tuples of (RoleObject, StaffObject) pairs for each weekday
    """
    global weekSchedule # global for other functions to access.
    weekSchedule = []
    for day in rolesOfWeek:
        daySchedule = []
        for role in day:
            roleStaffPair = (role, random.choice(staffList))
            daySchedule.append(roleStaffPair)
        weekSchedule.append(daySchedule)
    return weekSchedule


def scheduleView(schedule):
    """print schedule to screen"""
    for day in range(len(schedule)):
        headerDate= Weekday(day)
        print(f'{headerDate}')
        for roleStaffPair in schedule[day]:
            role = roleStaffPair[0]
            staff = roleStaffPair[1]
            if role.day == headerDate:
                print(f'{role.name}: {staff.name}')

