import main
import datetime
import os
import logging
logging.basicConfig(filename='debug.log', filemode='w', level=logging.DEBUG)

from classes import Weekdays, Role, Staff
from input.worlddata import qualifiedStaff_Dec12

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

                availability = setAvailability() 

                staffObject = Staff(name=name, maxShifts=int(maxShifts), availability=availability, rolePreference=rolePreference)
                weekStaff.append(staffObject)

        return weekStaff


def setAvailability():
    allCallTimes = set(Role.callTimes.values())
    availability = {
        Weekdays.MONDAY: [allCallTimes], #Question: is there a way to create this dict with automatically settings keys to one of each Weekdays?
        Weekdays.TUESDAY: [allCallTimes],
        Weekdays.WEDNESDAY: [allCallTimes],
        Weekdays.THURSDAY: [allCallTimes],
        Weekdays.FRIDAY: [allCallTimes],
        Weekdays.SATURDAY: [allCallTimes],
        Weekdays.SUNDAY: [allCallTimes]
    }

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
            day = Weekdays[line.upper().strip()]

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
            rolesOfDay = [Role(name=roleName.lower(), day=weekday) for roleName in roles]
        for role in rolesOfDay: #lazy 'fix' to not store a list of lists for each weekday.
            rolesOfWeek.append(role)
    return rolesOfWeek

def printWeekSchedule(schedule):
	for day in Weekdays:
		print(day.name)
		dayPairs = [pair for pair in schedule if pair[0].day == day]
		for pair in dayPairs:
			print(pair[0].name, pair[1].name)

def printDaySchedule(schedule, weekday):
	dayPairs = [pair for pair in schedule if pair[0].day == weekday]
	print(weekday.name)
	for pair in dayPairs:
		print(pair[0].name, pair[1].name)


def logStats(roleStaffPairs, staffCollection):
	for staff in staffCollection:
		logging.debug(f'{staff} shifts remaining: {staff.shiftsRemaining(roleStaffPairs)}')

def createSchedule_debug(roleCollection, staffCollection):
	"""returns a 'schedule' as a list of (role,staff) tuple pairs"""
	roleCollection = qualifiedStaff_Dec12.setQualifiedStaff(roleCollection, staffCollection)
	roleCollection.sort(key=lambda role: len(role.qualifiedStaff)) #sort roles by 'tightest' qualificiation list first.

	roleStaffPairs = []
	for role in roleCollection: # select the first role of the ordered role collection.
		availableStaff = [staff for staff in role.qualifiedStaff if staff.isAvailable(role)] # from the qualified staff list, get a list of all qualified staff who are available.
		availableStaff = [staff for staff in availableStaff if staff not in main.staffWorkingToday(roleStaffPairs, role.day)] # narrow list to staff not already scheduled that day.
		availableStaff = [staff for staff in availableStaff if staff.shiftsRemaining(roleStaffPairs) > 0] # adhearing to maxShifts attribute
		logging.info(f'{role} on {role.day.name} staff available, qualified, and not yet working: {availableStaff}')
		if availableStaff == []:
			logging.warning(f'No staff for {role} on {role.day.name}')
			unassigned = Staff(name='Unassigned',maxShifts=None, availability=None) #pair with Unassigned
			roleStaffPairs.append((role,unassigned))
			continue
		availableStaff = [staff for staff in availableStaff if role.name in staff.rolePreference] #narrow list down to include staff who has 'preference' for role
		logging.info(f'narrow list to include role preference {availableStaff}')
		if availableStaff == []:
			logging.warning(f'no prefered staff for {role}')
			unassigned = Staff(name='Unassigned',maxShifts=None, availability=None) #pair with Unassigned
			roleStaffPairs.append((role,unassigned))
			continue
		availableStaff.sort(key = lambda staff: staff.shiftsRemaining(roleStaffPairs), reverse=True)# sort the list of available staff with highest shifts remaining at the front.
		staff = availableStaff[0]
		roleStaffPairs.append((role,staff))

	logStats(roleStaffPairs, staffCollection)
	return roleStaffPairs

roleList = compileRoles('worlddata/roles_Dec12_Week.txt')
staffList = compileStaff('worlddata/staff_Dec12_Week.txt')

schedule = createSchedule_debug(roleList, staffList)

printWeekSchedule(schedule)