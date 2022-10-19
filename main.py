# WIP: Scheduler for Kiki's restaurant

from enum import Enum

class Weekday(Enum):
	MONDAY = 0
	TUESDAY = 1
	WEDNESDAY = 2
	THURSDAY = 3
	FRIDAY = 4
	SATURDAY = 5
	SUNDAY = 6

class Role:
	def __init__(self, name, day, callTime=None): 
		self.name = name

		#enum of weekday
		self.day = day
  
		#default values for callTime based on role:
		callTimes = {
			'lunch': '10:30 AM',
			'brunch': '10:30 AM',
			'bbar': '4:30 PM',
			'vbar': '4:30 PM',
			'middle': '6:00 PM',
			'back': '6:00 PM',
			'veranda': '4:30 PM',
			'front': '4:30 PM',
			'aux': '6:00 PM',
			'shermans': '4:30 PM',
			'swing': '1:00 PM'
		}
		self.callTime = callTimes.get(name, callTime)
		if self.callTime is None:
			raise ValueError('Provide recognized role name or call time.')

class Employee:
	#max number of shifts
	#availability
	#for each role, aptitude
	#name
	def __init__(self, name, max_shifts, availability):
		self.name = name
		self.max_shifts = max_shifts
		self.availability = availability


	def shiftsRemaining(self, schedule):
		'''employee's shifts remaining is max_shifts - the number of shifts they are currently in the schedule for'''
		remainingShifts = self.max_shifts
		for shift in schedule:
			if self in shift:
				remainingShifts -= 1
		return remainingShifts

	"""
	{
		"Monday": {"Aux", "Lunch", "Eve"},
		"Tuesday": {"Lunch"},
		"Wednesday": None,
		"Thursday": None,
		"Friday": {"Aux", "Lunch", "Eve"},
		"Saturday": {"Aux", "Lunch", "Eve"},
		"Sunday": {"Aux", "Lunch"}
	}
	"""

def can_take_on_role(employee, role, schedule=None): # Chaining the schedule in here to get it to 'shifts remaining' does not seem optimal.
													# TODO: fix this
	#number of shifts available > 0
	if not employee.shiftsRemaining(schedule) > 0:
		return False
	
	# employee must have availabilty for the role
	if role.name.lower() not in employee.availability[role.day]:
		return False
	
	return True

def employee_role_rank(employee, schedule):
	#highest aptitude for role
	#shouldn't have another role that day (not a dealbreaker)
	#if employee in schedule:
		# don't assign them another role for that day.
		# so. role.day is checked with employee's avail key.
		#TODO

	return employee.shiftsRemaining(schedule)


def createSchedule(roles, employees):
	week_schedule = []
	for role in roles:
		#find all the available employees for role
		possible_employees = [employee for employee in employees if can_take_on_role(employee, role, week_schedule)] # the week_schedule chaining here is not ideal.
		#assign the best employee for the role
		try:
			role_and_employee = (role, max(possible_employees, key=lambda employee: employee_role_rank(employee, week_schedule) )) # this is mostly here to play with a lambda.
		except ValueError:
			role_and_employee = (role, Employee('Unassinged',99,{}))
		week_schedule.append(role_and_employee)

	return week_schedule

roles = [
	Role(name="lunch", day=Weekday(0)), 
	Role(name="back", day=Weekday(0)), 
	Role(name="aux", day=Weekday(0)),
	Role(name="lunch", day=Weekday(1))
]

employees = [
	Employee(
		name="Sil", 
		max_shifts=2,
		availability={
			Weekday(0): {"aux", "lunch", "eve"}, # Question: Why a set?
			Weekday(1): {"lunch"}
		}
	),
	Employee(
		name="Mathew",
		max_shifts=3,
		availability={
			Weekday(0): {"back"},
			Weekday(1): {}
		}
	),
	Employee(
		name="Ashlynn",
		max_shifts=4,
		availability={
			Weekday(0): {"lunch"},
			Weekday(1): {}
		}
	)
]

weekly_schedule = createSchedule(roles, employees)
print(weekly_schedule)
for re in weekly_schedule:
	print(re[0].name, re[0].day, re[1].name)
	print(re[1].shiftsRemaining(weekly_schedule))