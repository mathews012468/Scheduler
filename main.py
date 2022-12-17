from enum import Enum
import datetime

#Things to do/discuss:
#Feedback/sanity check for current functions.
#Schedule as an object seems appealing, though unsure why.
#Merge into master branch

#Further ahead:
#How/where to store data for RolePreference

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
		self.callTime = callTimes.get(name, callTime)
		if self.callTime == None:
			raise ValueError(f'provide callTime for {self.name}')
		
	def __repr__(self):
		return "{self.__class__.__name__}({self.name},{self.day})".format(self=self)

	def __str__(self):
		return f"{self.name}"

class Staff:
	def __init__(self, name, maxShifts, availability):
		self.name = name
		self.maxShifts = maxShifts
		self.availability = availability

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
		availableStaff = [staff for staff in staffCollection if staff.isAvailable(role) and staff not in scheduledStaff]
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


def setQualifiedStaff(roleCollection, staffCollection):
	#current hack-around.
	#Desired format is to have default value of a Role object be 'staffCollection' instead of current None.
	for role in roleCollection:
		if role.name == 'door':
			role.qualifiedStaff = ['Glenn, Fernanda, Rose, Zoey']
		else:
			role.qualifiedStaff = staffCollection
	return roleCollection



#The first pass is to have all roles paired with a staff.
#That is the goal to get to, with data from previously scheduled weeks.

#Select the role with the shortest list of qualified staff.
#get list of the role's qualified staff that is avaiable and not yet scheduled that day of the week.
#order the staff list by shifts remaining
#pair the first staff from the qualified staff list with the role.

#when no staff can be found given the above criterea:
	#log: no available staff found for {role}
	#pair role with 'Unassigned'
	#continue to next role in the role collection.


def createSchedule(roleCollection, staffCollection):
	"""returns a 'schedule' as a list of (role,staff) tuple pairs"""
	roleCollection = setQualifiedStaff(roleCollection, staffCollection) 
	#now proceed with pairing each role.

	roleStaffPairs = []
	for role in roleCollection: # select the first role of the role collection.
		availableStaff = [staff for staff in staffCollection if staff.isAvailable(role) and staff.isQualified(role)] # from the staff collection, get a pool of all staff who are available for the selected role's call time.
		if availableStaff == []:
			raise RuntimeError(f'No staff available for {role}')
		availableStaff.sort(key = lambda staff: shiftsRemaining(staff, roleStaffPairs), reverse=True)# order the pool of available staff with highest shifts remaining at the front.
		for staff in availableStaff: # select the first staff from the ordered pool.
			if staff not in staffWorkingToday(roleStaffPairs, role.day):
				roleStaffPairs.append((role,staff)) #pair selected staff with selected role.
				break
			if staff == availableStaff[-1]:
				unassigned = Staff(name='unassigned',maxShifts=None, availability=None)
				roleStaffPairs.append((role,unassigned))
			else:
				continue

	#sort through unassigned roles?



	#TODO:
	
	#test ideas
#are there any doubles?
#does anyone exceed their maxshifts?

#__str__
#__repr__
