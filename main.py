from enum import Enum
import datetime
import logging
logging.basicConfig(filename='debug.log', filemode='w', level=logging.DEBUG)

# Un-hardcode Staff.rolepreferences
# a solution for setQualifiedStaff

#role selection through workdays


class Weekdays(Enum):
	MONDAY = 0
	TUESDAY = 1
	WEDNESDAY = 2
	THURSDAY = 3
	FRIDAY = 4
	SATURDAY = 5
	SUNDAY = 6


class Role:
	def __init__(self, name, day, callTime=None, qualifiedStaff=None):
		self.name = name
		self.day = day
		self.qualifiedStaff = qualifiedStaff

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
		self.callTime = callTimes.get(name, callTime)
		if self.callTime == None:
			raise ValueError(f'provide callTime for {self.name}')
		
	def __repr__(self):
		return "{self.__class__.__name__}({self.name},{self.day})".format(self=self)

	def __str__(self):
		return f"{self.name}"

class Staff:
	def __init__(self, name, maxShifts, availability, rolePreference=None, doubles=False):
		self.name = name
		self.maxShifts = maxShifts
		self.availability = availability

		#TODO: un-hardcode (softcode?) this.
		rolePreferences = {
			'Staff4':['door']
		}
		allRoles = [
		'lunch', 'brunch', 'brunchdoor', 'swing', 'FMN', 'shermans',
		'veranda', 'outside', 'bbar', 'vbar', 'front', 'uber', 'door',
		'back', 'middle', 'shermans6pm', 'aux'
		]

		self.rolePreference = rolePreferences.get(name, allRoles)
		

	def __repr__(self):
		return "{self.__class__.__name__}({self.name},{self.maxShifts})".format(self=self)

	def __str__(self):
		return f"{self.name}"

	def isAvailable(self, role):
		dayAvailability = self.availability[role.day]
		for i in range(0, len(dayAvailability), 2): # iterate through dayAvailability in 'chunks' of 2
			availTimes = dayAvailability[i:i+2]
			startTime = availTimes[0]
			endTime = availTimes[1]
			if role.callTime >= startTime and role.callTime <= endTime:
				return True
			else:
				continue
		return False

	def isQualified(self, role):
		if self not in role.qualifiedStaff:
			return False
		return True


def pairAvailableStaff(roleCollection, staffCollection):
	roleStaffPairs = []
	for role in roleCollection: # select the first role of the role collection.
		availableStaff = [staff for staff in staffCollection if staff.isAvailable(role) and staff.isQualified(role)] # from the staff collection, get a pool of all staff who are available for the selected role's call time.
		if availableStaff == []:
			raise RuntimeError(f'No staff available for {role}')
		availableStaff.sort(key = lambda staff: shiftsRemaining(staff, roleStaffPairs), reverse=True)# order the pool of available staff with highest shifts remaining at the front.
		staff = availableStaff[0] # select the first staff from the ordered pool.
		roleStaffPairs.append((role,staff))
	return roleStaffPairs


def shiftsRemaining(staff, roleStaffPairs):
	shiftCount = 0
	for pair in roleStaffPairs:
		if pair[1] == staff:
			shiftCount += 1
	return staff.maxShifts - shiftCount


def staffDoubles(roleStaffPairs):
	"""
	take in current schedule, list of (role, staff)
	return list of indices of staff that are doubled in a day in that list
	"""
	
	#if staff has already worked that day, then it's a double
	doubleIndices = []
	staffDays = set() #set of staff day pairs
	for index, pair in enumerate(roleStaffPairs):
		staff = pair[1]
		day = pair[0].day
		staffDay = (staff, day)

		if staffDay in staffDays:
			doubleIndices.append(index)
		else:
			staffDays.add(staffDay)
	return doubleIndices


def repairDoubles(roleStaffPairs, staffCollection):
	doubleIndices = staffDoubles(roleStaffPairs)
	for index in doubleIndices:
		role = roleStaffPairs[index][0]
		scheduledStaff = staffWorkingToday(roleStaffPairs, role.day)
		availableStaff = [staff for staff in staffCollection if staff.isAvailable(role) and staff.isQualified(role) and staff not in scheduledStaff]
		if availableStaff == []:
			raise RuntimeError(f'No staff avaialbe to repair {role.name}')
		availableStaff.sort(key = lambda staff: shiftsRemaining(staff, roleStaffPairs), reverse=True)
		
		#repair the role at index with new staff.
		newPair = list(roleStaffPairs[index]) #tuple to list
		newPair[1] = availableStaff[0] # repair staff
		roleStaffPairs[index] = newPair # insert new pairing
	return roleStaffPairs


def staffWorkingToday(roleStaffPairs, weekday):
	scheduledStaff = set()
	for pair in roleStaffPairs:
		if pair[0].day == weekday:
			scheduledStaff.add(pair[1])
	return scheduledStaff

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


def sortKey_shiftsRemaining(staffList, roleStaffPairs):
	"""seperate function for testing"""
	staffList.sort(key = lambda staff: shiftsRemaining(staff, roleStaffPairs), reverse=True)
	return staffList

def sortKey_qualifiedStaff(roleCollection):
	"""seperate function for testing"""
	roleCollection.sort(key=lambda role: len(role.qualifiedStaff))
	return roleCollection

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
	#TODO: A 'softcode' solution for this
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


def createSchedule_noDoubles(roleCollection, staffCollection):
	"""returns a 'schedule' as a list of (role,staff) tuple pairs"""
	roleCollection = setQualifiedStaff(roleCollection, staffCollection) 
	#TODO: Sort by loop of each day in weekday [role.monday, role.tuesday, role.wednesday, role.thursday, role.friday, role.saturday, role.sunday, role.monday...etc]
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

def staffKey(staff, role, roleStaffPairs):
	"""
	return an int representing the rank value of a staff for given role
	larger int is a higher ranking
	"""
	key = 1000 #base value of rank
	key += (shiftsRemaining(staff, roleStaffPairs) * 100) # add value of 100 for each of this staff's shift remaining
	if not staff.isAvailabile(role):
		key -= 1000 # subtract value of 1,000 when staff does not have availabilty for this role's callTime
	if not role.name in staff.rolePreference:
		key -= 100 # subtract value of 100 when this role is not in this staff's role prefrence
	if staff in staffWorkingToday(roleStaffPairs, role.day):
		key -= 500 # subtract value of 500 when this staff is already scheduled to work this weekday
	if not staff in role.qualifiedStaff:
		key -= 1000 # subtract value of 1,000 when this staff is not qualified for this role
	
	staff._key = key #store key in staff '_key' attribute
	#Question: You can create an attribute without defining it in the class initialization?
	#Does it matter that it's '_private' in this case?
	return key

def createSchedule(roleCollection, staffCollection):
	roleCollection = setQualifiedStaff(roleCollection, staffCollection)
	roleCollection.sort(key = lambda role: len(role.qualifiedStaff))

	roleStaffPairs = []
	for role in roleCollection:
		staff = max(staffCollection, key = lambda staff: staffKey(staff, role, rolesStaffPairs))
		newPair = (role, staff)
		if staff._key <= -1000:
			logging.info(f'no suitable staff found for {role}')
			unassigned = Staff(name='Unassigned',maxShifts=None, availability=None)
			newPair = (role, unassigned)
		roleStaffPairs.append(newPair)

	logStats(roleStaffPairs)
	return roleStaffPairs

def alternateStaffForRole(roleStaffPairs, index, staffCollection, cutOff=-500):
	"""Once roleStaffPairs have been assigned,
	return a list of alternate staffing options for a roleStaffPair at given index
	"""
	pairToBeReassigend = roleStaffPairs[index]
	currentRole = pairToBeReassigend[0]
	currentStaff = pairToBeReassigend[1]
	alternateStaff = [staff for staff in staffCollection if staffKey(staff,currentRole,roleStaffPairs) >= cutOff and staff != currentStaff]

	return alternateStaff




def createSchedule_doubles(roleCollection, staffCollection):
	roleCollection = setQualifiedStaff(roleCollection, staffCollection) 
	roleCollection.sort(key=lambda role: len(role.qualifiedStaff))
	schedule = pairAvailableStaff(roleCollection, staffCollection)
	schedule = repairDoubles(schedule, staffCollection)
	logStats(schedule, staffCollection)
	return schedule

def logStats(roleStaffPairs, staffCollection):
	for staff in staffCollection:
		logging.debug(f'{staff} shifts remaining: {shiftsRemaining(staff, roleStaffPairs)}')


	#test ideas
#are there any doubles?
#does anyone exceed their maxshifts?

#__str__
#__repr__
