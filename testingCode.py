import main
import datetime
import os

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

                line = f.readline() # move to role prefence line
                rolePreference = eval(line.split(':')[1].strip())

                line = f.readline() # move to request line
                requestLines = []
                while True: #store the next set of lines
                    line = f.readline()
                    if line.startswith('\n'):
                        break
                    requestLines.append(line.strip())
                availability = setAvailability(requestLines) 

                staffObject = main.Staff(name=name, maxShifts=int(maxShifts), availability=availability, rolePreference=rolePreference)
                weekStaff.append(staffObject)

        return weekStaff

def setAvailability(requestLines):
    """set availability from staff request lines
    input: list of stripped request lines from staff .txt file
    returns: dictionary for Staff object availabiltiy
    """
    availability = {
            main.Weekdays.MONDAY: [datetime.time(hour=8),datetime.time(hour=23)],
            main.Weekdays.TUESDAY: [datetime.time(hour=8),datetime.time(hour=23)],
            main.Weekdays.WEDNESDAY: [datetime.time(hour=8),datetime.time(hour=23)],
            main.Weekdays.THURSDAY: [datetime.time(hour=8),datetime.time(hour=23)],
            main.Weekdays.FRIDAY: [datetime.time(hour=8),datetime.time(hour=23)],
            main.Weekdays.SATURDAY: [datetime.time(hour=8),datetime.time(hour=23)],
            main.Weekdays.SUNDAY: [datetime.time(hour=8),datetime.time(hour=23)]
            }

    for line in requestLines:
        day, requestTimes = line.split(':')
        requestTimes = [hours for hours in requestTimes.split(',')]
        availability[main.Weekdays[day.upper()]] =[] # clear Schedule.Weekdays's default availability

        while requestTimes != []:
            start, end = requestTimes[:2]
            del requestTimes[:2]
            startHour, startMinute = start.split('.')
            endHour, endMinute = end.split('.')

            availability[main.Weekdays[day.upper()]].append(datetime.time(int(startHour),int(startMinute) ) )
            availability[main.Weekdays[day.upper()]].append(datetime.time(int(endHour),int(endMinute) ) )

    return availability


def compileRoles(roleFileName):
    """input: .txt file containing names of roles and associated Weekdays
    Output: A list of dictionaries for each Weekdays.
    Dictionary[key] = Weekdays.Enum
    Dictionary[value] = list of role names
    """
    roleFilePath = os.path.join('input', roleFileName)
    weekRoleNames=[]
    with open(roleFilePath) as file:
        while line := file.readline():
            if line == '\n' or line.startswith('#'): #ignore empty and #comment lines
                continue
            day = main.Weekdays[line.upper().strip()]

            line = file.readline()
            roles = [role.strip() for role in line.split(',')]

            weekRoleNames.append({day: roles})
    #create list of Role objects from weekRoleNames
    return createRoles(weekRoleNames)

def createRoles(compiledRoles):
    """Create Role Objects from compiled roles.txt input
    Input: List of dictionaries from compileWeek()
    Output: A list of lists containing Role Objects for each Weekdays
    """
    rolesOfWeek = []
    for dict in compiledRoles:
        for weekday ,roles in dict.items():
            rolesOfDay = [main.Role(name=roleName.lower(), day=weekday) for roleName in roles]
        for role in rolesOfDay: #lazy 'fix' to not store a list of lists for each weekday.
            rolesOfWeek.append(role)
    return rolesOfWeek

def printWeekSchedule(schedule):
	for day in main.Weekdays:
		print(day.name)
		dayPairs = [pair for pair in schedule if pair[0].day == day]
		for pair in dayPairs:
			print(pair[0].name, pair[1].name)

def printDaySchedule(schedule, weekday):
	dayPairs = [pair for pair in schedule if pair[0].day == weekday]
	print(weekday.name)
	for pair in dayPairs:
		print(pair[0].name, pair[1].name)

roleList = compileRoles('worlddata/roles_Dec12_Week.txt')
staffList = compileStaff('worlddata/staff_Dec12_Week.txt')

schedule = main.createSchedule(roleList, staffList)

printWeekSchedule(schedule)