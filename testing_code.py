import reWrite, ast, datetime
from pathlib import Path



def getRequest(line):
    """ get int of start and end request times from string"""
    requestTime = [8,23] #pre-filled with default values
    requestSplit = line.split('-')
    startDigit = [char for char in requestSplit[0] if char.isdigit()] #find digits before the dash
    if startDigit: #if list comp is not empty
        startDigit = int(''.join(startDigit))
        if startDigit != 12 and requestSplit[0].strip().endswith('pm'):
            startTime = int(startDigit) + 12 #add 12 for 24hr time
            requestTime[0] = startTime
        else:
            startTime = int(startDigit)
            requestTime[0] = startTime

    endDigit = [char for char in requestSplit[1] if char.isdigit()] #find digits after the dash
    if endDigit:
        endDigit = int(''.join(endDigit))
        if endDigit != 12 and requestSplit[1].strip().endswith('pm'):
            endTime = int(endDigit) + 12
            requestTime[1] = endTime
        else:
            endTime = int(endDigit)
            requestTime[1] = endTime 
    return requestTime


def setRequests(file, staff):
    """set staff.availability according to request input"""
    staff.availability = { #set default full availability
            reWrite.Weekday.MONDAY: [datetime.time(8),datetime.time(23)],
            reWrite.Weekday.TUESDAY: [datetime.time(8),datetime.time(23)],
            reWrite.Weekday.WENDESDAY: [datetime.time(8),datetime.time(23)],
            reWrite.Weekday.THURSDAY: [datetime.time(8),datetime.time(23)],
            reWrite.Weekday.FRIDAY: [datetime.time(8),datetime.time(23)],
            reWrite.Weekday.SATURDAY: [datetime.time(8),datetime.time(23)],
            reWrite.Weekday.SUNDAY: [datetime.time(8),datetime.time(23)]
            }
    line = file.readline()
    print(line + 'inside setRequests') # Help.


def compileStaff(staffFileName):
    """compile staff from .txt file containing staff data"""
    staffFilePath = Path.cwd() / 'testing/input' / staffFileName
    with open(staffFilePath) as f:
        weekStaff = []
        while line := f.readline(): # can you explain this? I can't seem to grasp how this works.
            if line.lower().startswith('name'):
                staffName = line.split(':')[1].strip()

                line = f.readline()
                print(line + 'hey')
            if line.lower().startswith('shifts'):
                maxShifts = int(line.split(':')[1].strip())

                staffObject = reWrite.Staff(name=staffName)

            if line.lower().startswith('requests'):
                setRequests(f, staffObject)

                weekStaff.append(staffObject)

        return weekStaff

compileStaff('staff_test.txt')


def compileRoles(roleFileName):
    """input: .txt file containing names of roles and associated weekday
    Output: A list of dictionaries for each weekday.
    Dictionary[key] = Weekday.Enum
    Dictionary[value] = list of role names
    """
    roleFilePath = Path.cwd() / 'testing/input' / roleFileName
    weekRoleNames=[]
    with open(roleFilePath) as file:
        while line := file.readline():
            if line == '\n' or line.startswith('#'): #ignore empty and #comment lines
                continue
            day = reWrite.Weekday[line.upper().strip()] #line -> Weekday Enum

            line = file.readline() #I don't actually understand how and why this works.
            roles = [role.strip() for role in line.split(',')]

            weekRoleNames.append({day: roles})
    return weekRoleNames


weekRoleNames = compileRoles('roles_monday.txt') #bah, the naming here is a mess.
#rolesOfWeek = reWrite.createRoles(weekRoleNames)

#schedule = reWrite.createWeekSchedule(rolesOfWeek, staffList)

#reWrite.scheduleView(schedule)