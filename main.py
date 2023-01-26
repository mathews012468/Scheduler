from classes import Staff

# main is sparse and clean.
# All the indecision has been shoved under the rug of testingCode.

def staffWorkingToday(roleStaffPairs, weekday):
	scheduledStaff = set()
	for pair in roleStaffPairs:
		if pair[0].day == weekday:
			scheduledStaff.add(pair[1])
	return scheduledStaff


def setAvailability(staff, input):
	"""with input from request form, update staff availability dictionary"""
	staff.availability = dict(input)
	pass


def createSchedule(roleCollection, staffCollection):
	"""
	returns a 'schedule as a list of (role,staff) pair tuples
	Assumes Role and Staff objects have been compiled from spreadsheet database
	"""
	roleCollection.sort(key=lambda role: len(role.qualifiedStaff))
	roleStaffPairs = []
	for role in roleCollection:
		availableStaff = [staff for staff in staffCollection if staff.name in role.qualifiedStaff and staff.isAvailable(role) and staff not in staffWorkingToday(roleStaffPairs, role.day)] # I don't like how long this line is.
		availableStaff = [staff for staff in availableStaff if role.name in staff.rolePreference]
		availableStaff = [staff for staff in availableStaff if staff.shiftsRemaining(roleStaffPairs) > 0]
		if availableStaff == []:
			unassigned = Staff(name='Unassigned',maxShifts=None, availability=None)
			roleStaffPairs.append((role,unassigned))
			continue
		availableStaff.sort(key = lambda staff: staff.shiftsRemaining(roleStaffPairs), reverse=True)
		staff = availableStaff[0]
		roleStaffPairs.append((role,staff))
	return roleStaffPairs