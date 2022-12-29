from classes import Weekdays, Role, Staff
import logging
logging.basicConfig(filename='debug.log', filemode='w', level=logging.DEBUG)

from input.worlddata import qualifiedStaff_Dec12

#TODO:

#figure out this qualifiedStaff thing

#Re-write weekdaySorting in way that's not destructive to roleCollection


def shiftsRemaining(staff, roleStaffPairs):
	shiftCount = 0
	for pair in roleStaffPairs:
		if pair[1] == staff:
			shiftCount += 1
	return staff.maxShifts - shiftCount


def staffWorkingToday(roleStaffPairs, weekday):
	scheduledStaff = set()
	for pair in roleStaffPairs:
		if pair[0].day == weekday:
			scheduledStaff.add(pair[1])
	return scheduledStaff


def sortWeekdayPattern(roleCollection):
	"""
	pattern the roleCollection by loop of each day in weekday
	[role.monday, role.tuesday, role.wednesday, role.thursday, role.friday, role.saturday, role.sunday, role.monday...etc]
	"""
	patternedList = []
	while roleCollection != []:
		for day in Weekdays:
			for role in roleCollection:
				if role.day == day:
					patternedList.append(role)
					roleCollection.remove(role)
					break
	return patternedList
	

def setQualifiedStaff(roleCollection, staffCollection):
	#temp solution. Specific qualifed list for 'door', 'brunchdoor' and 'FMN'
	for role in roleCollection:
		if role.name == 'door':
			doorStaff = ['Staff1', 'Staff2', 'Staff3', 'Staff4']
			doorList = [staff for staff in staffCollection if staff.name in doorStaff] #get staff objects
			role.qualifiedStaff = doorList
		if role.name == 'brunchdoor':
			brunchdoorStaff = ['Staff2', 'Staff1', 'Staff5']
			brunchdoorList = [staff for staff in staffCollection if staff.name in brunchdoorStaff]
			role.qualifiedStaff = brunchdoorList
		if role.name == 'FMN':
			FMNStaff = ['Staff5']
			FMNList = [staff for staff in staffCollection if staff.name in FMNStaff]
			role.qualifiedStaff = FMNList
		if role.qualifiedStaff == None:
			role.qualifiedStaff = staffCollection
	return roleCollection


def createSchedule(roleCollection, staffCollection):
	"""returns a 'schedule' as a list of (role,staff) tuple pairs"""
	roleCollection = qualifiedStaff_Dec12.setQualifiedStaff(roleCollection, staffCollection)
	roleCollection = sortWeekdayPattern(roleCollection) # to balance role staff pairing across the week
	roleCollection.sort(key=lambda role: len(role.qualifiedStaff)) #sort roles by 'tightest' qualificiation list first.

	roleStaffPairs = []
	for role in roleCollection: # select the first role of the ordered role collection.
		availableStaff = [staff for staff in role.qualifiedStaff if staff.isAvailable(role)] # from the qualified staff list, get a list of all staff who are available.
		availableStaff = [staff for staff in availableStaff if shiftsRemaining(staff, roleStaffPairs) > 0] # adhearing to maxShifts attribute
		availableStaff = [staff for staff in availableStaff if role.name in staff.rolePreference]
		if availableStaff == []:
			logging.info(f'No staff with availabilty for {role}')
			unassigned = Staff(name='Unassigned',maxShifts=None, availability=None) #pair with Unassigned
			roleStaffPairs.append((role,unassigned))
			continue

		availableStaff.sort(key = lambda staff: shiftsRemaining(staff, roleStaffPairs), reverse=True)# order the list of available staff with highest shifts remaining at the front.
		for staff in availableStaff: # select the first staff from the ordered pool.
			if staff not in staffWorkingToday(roleStaffPairs, role.day): # no doubles on this pass.
				roleStaffPairs.append((role,staff))
				break
			if staff == availableStaff[-1]: #end of list reached with no pairing found.
				logging.info(f'no staff available without double for {role} on {role.day.name}')
				logging.info(f'{availableStaff}')
				unassigned = Staff(name='Unassigned',maxShifts=None, availability=None)
				roleStaffPairs.append((role,unassigned))
			else:
				continue # select next staff from list

	logStats(roleStaffPairs, staffCollection)
	return roleStaffPairs


def logStats(roleStaffPairs, staffCollection):
	for staff in staffCollection:
		logging.debug(f'{staff} shifts remaining: {shiftsRemaining(staff, roleStaffPairs)}')