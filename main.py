import random, datetime, os
from enum import Enum

class Weekday(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

#For the moment, this seems like using a class as a module, avoiding a circular import. 
class ProcessInput:
    """Contains functions to compile roles and compile staff from input.txt files"""

    def compileStaff(staffFileName):
        """compile staff from .txt file containing staff data"""
        staffFilePath = os.path.join('input', staffFileName)
        with open(staffFilePath) as f:
            weekStaff = []
            while line := f.readline():

                if line.lower().startswith('name'):
                    name = line.split(':')[1].strip()

                    line = f.readline() # move to shift line
                    maxShifts = line.split(':')[1].strip()

                    line = f.readline() # move to request line
                    requestLines = []
                    while True: #store the next set of lines
                        line = f.readline()
                        if line.startswith('\n'):
                            break
                        requestLines.append(line.strip())
                    availability = ProcessInput.setAvailability(requestLines) 

                    staffObject = Staff(name, int(maxShifts), availability)
                    weekStaff.append(staffObject)

            return weekStaff

    def setAvailability(requestLines):
        """set availability from staff request lines
        input: list of stripped request lines from staff .txt file
        returns: dictionary for Staff object availabiltiy
        """
        availability = {
                Weekday.MONDAY: [datetime.time(hour=8),datetime.time(hour=23)],
                Weekday.TUESDAY: [datetime.time(hour=8),datetime.time(hour=23)],
                Weekday.WEDNESDAY: [datetime.time(hour=8),datetime.time(hour=23)],
                Weekday.THURSDAY: [datetime.time(hour=8),datetime.time(hour=23)],
                Weekday.FRIDAY: [datetime.time(hour=8),datetime.time(hour=23)],
                Weekday.SATURDAY: [datetime.time(hour=8),datetime.time(hour=23)],
                Weekday.SUNDAY: [datetime.time(hour=8),datetime.time(hour=23)]
                }

        for line in requestLines:
            weekday, requestTimes = line.split(':')
            requestTimes = [hours for hours in requestTimes.split(',')]
            availability[Weekday[weekday.upper()]] =[] # clear weekday's default availability

            while requestTimes != []:
                start, end = requestTimes[:2]
                del requestTimes[:2]
                startHour, startMinute = start.split('.')
                endHour, endMinute = end.split('.')

                availability[Weekday[weekday.upper()]].append(datetime.time(int(startHour),int(startMinute) ) )
                availability[Weekday[weekday.upper()]].append(datetime.time(int(endHour),int(endMinute) ) )

        return availability

    def compileRoles(roleFileName):
        """input: .txt file containing names of roles and associated weekday
        Output: A list of dictionaries for each weekday.
        Dictionary[key] = Weekday.Enum
        Dictionary[value] = list of role names
        """
        roleFilePath = os.path.join('input', roleFileName)
        weekRoleNames=[]
        with open(roleFilePath) as file:
            while line := file.readline():
                if line == '\n' or line.startswith('#'): #ignore empty and #comment lines
                    continue
                day = Weekday[line.upper().strip()]

                line = file.readline()
                roles = [role.strip() for role in line.split(',')]

                weekRoleNames.append({day: roles})
        #create list of Role objects from weekRoleNames
        return ProcessInput.createRoles(weekRoleNames)

    def createRoles(compiledRoles):
        """Create Role Objects from compiled roles.txt input
        Input: List of dictionaries from compileWeek()
        Output: A list of lists containing Role Objects for each weekday
        """
        rolesOfWeek = []
        for dict in compiledRoles:
            for weekday,roles in dict.items():
                rolesOfDay = [Role(name=roleName, day=weekday) for roleName in roles]
            rolesOfWeek.append(rolesOfDay)
        return rolesOfWeek


class Schedule:
    def __init__(self, roleInput, staffInput, week=None):
        """"Create schedule object from role and staff inputs
        roleInput = string filename.txt
        staffInput = string filename.txt """
        scheduleRoles = ProcessInput.compileRoles(roleInput)
        scheduleStaff = ProcessInput.compileStaff(staffInput)

        week = []
        for day in scheduleRoles:
            daySchedule = []
            for role in day:
                availableStaff = [staff for staff in scheduleStaff if isAvailable(role, staff)]
                roleStaffPair = (role, random.choice(availableStaff))
                daySchedule.append(roleStaffPair)
            week.append(daySchedule)

        self.week = week


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

def createRoles(compiledRoles):
    """Create Role Objects from compiled roles.txt input
    Input: List of dictionaries from compileWeek()
    Output: A list of lists containing Role Objects for each weekday
    """
    rolesOfWeek = []
    for dict in compiledRoles:
        for weekday,roles in dict.items():
            rolesOfDay = [Role(name=roleName, day=weekday) for roleName in roles]
        rolesOfWeek.append(rolesOfDay)
    return rolesOfWeek


def shiftsRemaining(staff, schedule):
    shiftsRemaining = staff.maxShifts
    flatSchedule = [pairs for day in schedule.week for pairs in day]
    shiftCount = 0
    for roleStaffPair in flatSchedule:
        if roleStaffPair[1] == staff:
            shiftsRemaining -= 1
    if shiftsRemaining < 0:
        raise ValueError(f'{staff.name} shiftsRemaing: {shiftsRemaining}')
    return shiftsRemaining


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



schedule = Schedule('roles_sixShifts.txt','staff_single.txt')
print(schedule.week)
print(schedule.week[0])
print(schedule.week[0][0])
print(schedule.week[0][0][1])

