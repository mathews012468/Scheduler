import main, datetime, os


def setAvailability(lines):
    """set availability from staff request lines
    input: list of lines from staff .txt file
    returns: dictionary for Staff object availabiltiy
    """
    availability = {
            main.Weekday.MONDAY: [datetime.time(hour=8),datetime.time(hour=23)],
            main.Weekday.TUESDAY: [datetime.time(hour=8),datetime.time(hour=23)],
            main.Weekday.WEDNESDAY: [datetime.time(hour=8),datetime.time(hour=23)],
            main.Weekday.THURSDAY: [datetime.time(hour=8),datetime.time(hour=23)],
            main.Weekday.FRIDAY: [datetime.time(hour=8),datetime.time(hour=23)],
            main.Weekday.SATURDAY: [datetime.time(hour=8),datetime.time(hour=23)],
            main.Weekday.SUNDAY: [datetime.time(hour=8),datetime.time(hour=23)]
            }

    for line in lines:
        weekday, requestTimes = line.split(':')
        requestTimes = [hours for hours in requestTimes.split(',')]
        availability[main.Weekday[weekday.upper()]] =[] # clear weekday's default availability

        while requestTimes != []:
            start, end = requestTimes[:2]
            del requestTimes[:2]
            startHour, startMinute = start.split('.')
            endHour, endMinute = end.split('.')

            availability[main.Weekday[weekday.upper()]].append(datetime.time(int(startHour),int(startMinute) ) )
            availability[main.Weekday[weekday.upper()]].append(datetime.time(int(endHour),int(endMinute) ) )

    return availability


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
                availability = setAvailability(requestLines) 

                staffObject = main.Staff(name, int(maxShifts), availability)
                weekStaff.append(staffObject)

        return weekStaff


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
            day = main.Weekday[line.upper().strip()]

            line = file.readline()
            roles = [role.strip() for role in line.split(',')]

            weekRoleNames.append({day: roles})
    return weekRoleNames

if __name__ == "__main__":

    staffList = compileStaff('staff_test.txt')
    weekRoleNames = compileRoles('roles_smallSample.txt')
    rolesOfWeek = main.createRoles(weekRoleNames)
    
    schedule = main.createWeekSchedule(rolesOfWeek, staffList)

    main.scheduleView(schedule)