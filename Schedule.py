# Goal:
# Take in a collection of roles
# Take in a collection of staff
# Return the collection of roles paired with staff

# Strategy for selecting staff:
# select the first role of the role collection.
# from the staff collection, get a pool of all staff who are available for the selected role's call time.
# order the pool of available staff with highest shifts remaining at the front.
# select the first staff from the ordered pool.
# pair selected staff with selected role.
# 
#
# Strategy for forming the scheduling:
# A seperate sweep for each criterea, such as Doubles, and Preference
# sweeps are called in order of 'importance'
# after last sweep, the 'finished' schedule is returned.

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
        self.callTime = callTimes.get(name)
        if self.callTime == None:
        	raise ValueError(f'{self.name} has no matching callTime')


class Staff:
	def __init__(self, name, maxShifts, availability):
		self.name = name
		self.maxShifts = maxShifts
		self.availability = availability

	def isAvailable(self, role):
		dayAvailability = self.availability[role.day]
		if role.callTime >= dayAvailability[0] and role.callTime <= dayAvailability[1]:
			return True
		return False




def pairAvailableStaff(roleCollection, staffCollection):
	roleStaffPairs = []
	for role in roleCollection: # select the first role of the role collection.
		availableStaff = [staff for staff in staffCollection if staff.isAvailable(role)] # from the staff collection, get a pool of all staff who are available for the selected role's call time.
		if availableStaff == []:
			raise RuntimeError(f'No staff available for {role}')
		availableStaff.sort(key = shiftsRemaining(roleStaffPairs)) # order the pool of available staff with highest shifts remaining at the front.
		staff = availableStaff[0] # select the first staff from the ordered pool.
		roleStaffPairs.append((role,staff)) #pair selected staff with selected role.
	return roleStaffPairs

def shiftsRemaining(staff, roleStaffPairs):
	shiftCount = 0
	for pair in roleStaffPairs:
		if pair[1] == staff:
			shiftCount += 1
	return staff.maxShifts - shiftCount

	

def repairDoubles(roleStaffPairs):
	for weekday in Weekdays:
		weekdayPairs = [pair for pair in roleStaffPairs if pair[0].day == weekday]
		for pairs in weekdayPairs:
			staffIndecies = [index for index, staff in enumerate(weekdayPairs) if staff == pairs[1]]
			if len(staffIndecies) > 1:
				doubles = staffIndecies[1:]


def formSchedule_00(roleCollection, staffCollection):
	schedule = []
	for role in roleCollection:
		availableStaff = [staff for staff in staffCollection if staff.isAvailable(role.callTime)]
		availableStaff.sort(key= shiftsRemaining)

		lowPriority = []
		for staff in availableStaff:
			if staff.isDouble(role):
				staff.append(lowPriority)
				continue
			else:
				schedule.append((role,staff))
				break
		lowPriority.sort(key = shiftsRemaining)
		schedule.append((role,lowPriority[0]))

	return schedule