# Clearing loose ends

#test and excercise pairAvailableStaff

from enum import Enum
import datetime

class Weekdays(Enum):
	MONDAY = 0
	TUESDAY = 1
	WEDNESDAY = 2
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


class Staff:
	def __init__(self, name, maxShifts, availability):
		self.name = name
		self.maxShifts = maxShifts
		self.availability = availability

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


def pairAvailableStaff(roleCollection, staffCollection):
	roleStaffPairs = []
	for role in roleCollection: # select the first role of the role collection.
		availableStaff = [staff for staff in staffCollection if staff.isAvailable(role)] # from the staff collection, get a pool of all staff who are available for the selected role's call time.
		if availableStaff == []:
			raise RuntimeError(f'No staff available for {role}')
		availableStaff.sort(key = lambda staff: shiftsRemaining(staff, roleStaffPairs), reverse=True)# order the pool of available staff with highest shifts remaining at the front.
		staff = availableStaff[0] # select the first staff from the ordered pool.
		roleStaffPairs.append((role,staff)) #pair selected staff with selected role.
	return roleStaffPairs

def shiftsRemaining(staff, roleStaffPairs):
	shiftCount = 0
	for pair in roleStaffPairs:
		if pair[1] == staff:
			shiftCount += 1
	return staff.maxShifts - shiftCount

	
#from the list of pairs,
# find all the staff that is doubled, which is in a day.
#[(role,staff), (role,staff), (role,staff)]

#we have to get a subset of days
#find the doubles in a day.

def doubledRoles(roleStaffPairs):
	"""
	take in current schedule, list of (role, staff)
	return list of indices of staff that are doubled in a day in that list
	"""
	
	#if staff has already worked that day, then it's a double
	doubleIndices = []
	staffDays = set() #set of staff day pairs
	for index, roleStaffPair in enumerate(roleStaffPairs):
		staff = roleStaffPair[1]
		day = roleStaffPair[0].day
		staffDay = (staff, day)

		if staffDay in staffDays:
			doubleIndices.append(index)
		else:
			staffDays.add(staffDay)
	return doubleIndices


def repairDoubles(roleStaffPairs, staffCollection):
	doubleIndices = doubledRoles(roleStaffPairs)
	for index in doubleIndices:
		role = roleStaffPairs[index][0]
		scheduledStaff = staffWorkingToday(roleStaffPairs, role.day)
		availableStaff = [staff for staff in staffCollection if staff.isAvailable(role) and staff not in scheduledStaff]
		availableStaff.sort(key = lambda staff: shiftsRemaining(staff, roleStaffPairs))
		
		#repair the role at index with new staff.
		newPair = list(roleStaffPairs[index]) #tuple to list
		newPair[1] = availableStaff[0] # repair staff
		roleStaffPairs[index] = newPair # insert new pairing

	return roleStaffPairs


def staffWorkingToday(roleStaffPairs, weekday):
	scheduledStaff = list()
	for pair in roleStaffPairs:
		if pair[0].day == weekday:
			scheduledStaff.append(pair[1])
	return scheduledStaff


	#Repair the doubles with staff who is availabe and not in the schedule to work that day.

	#then repair those doubles