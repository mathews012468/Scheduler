from enum import Enum
import datetime

import logging
logger = logging.getLogger(__name__)

class Weekdays(Enum):
	MONDAY = 0
	TUESDAY = 1
	WEDNESDAY = 2
	THURSDAY = 3
	FRIDAY = 4
	SATURDAY = 5
	SUNDAY = 6


class Role:

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

	def __init__(self, name, day, callTime=None, qualifiedStaff=None):
		self.name = name
		self.day = day
		self.qualifiedStaff = qualifiedStaff

		self.callTime = Role.callTimes.get(name, callTime)
		if self.callTime == None:
			raise ValueError(f'provide callTime for {self.name}')
		
	def __repr__(self):
		return "{self.__class__.__name__}({self.name},{self.day.name})".format(self=self)

	def __str__(self):
		return f"{self.name},{self.day.name}"
		

class Staff:
	def __init__(self, name, maxShifts, availability=None, rolePreference=None, doubles=False):
		self.name = name
		self.maxShifts = maxShifts
		self.availability = availability
		self.rolePreference = rolePreference
		self.doubles = doubles
		

	def __repr__(self):
		return "{self.__class__.__name__}({self.name})".format(self=self)

	def __str__(self):
		return f"{self.name}"

	def isAvailable(self, role):
		""""check role callTime is in staff availablity"""
		dayAvailability = self.availability[role.day]
		if role.callTime not in dayAvailability:
			return False
		return True

	def isQualified(self, role):
		if self.name not in role.qualifiedStaff:
			return False
		return True

	def isScheduled(self, role, schedule):
		for pair in schedule:
			if pair[0].day == role.day and pair[1] == self:
				logging.info(f'{self.name} already scheduled for {pair[0]}')
				return True
		return False
		

	def shiftsRemaining(self, roleStaffPairs):
		shiftCount = 0
		for pair in roleStaffPairs:
			if pair[1] == self:
				shiftCount += 1
		return self.maxShifts - shiftCount