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
		'door2':datetime.time(hour=18),
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

		#TODO: set up a cleaner way to do this
		rolePreferences = rolepreference_Dec12.rolePreferences
		allRoles = rolepreference_Dec12.allRoles

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