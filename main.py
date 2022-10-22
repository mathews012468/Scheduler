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

def isDouble(employee, schedule, role): # How to think about consolidating the same use of arguements here?
	for grouping in schedule:
		if not grouping[0].day == role.day or not grouping[1].name == employee.name:
			return False
	return True

def can_take_on_role(employee, role, schedule=None): # Chaining the schedule in here to get it to 'shifts remaining' does not seem optimal.
													# TODO: fix this
	#number of shifts available > 0
	if not employee.shiftsRemaining(schedule) > 0:
		return False
	
	# employee must have availabilty for the role
	if role.name.lower() not in employee.availability[role.day]:
		return False
	
	return True

def employee_role_rank(employee, schedule, role): #Oh, maybe I could pass in the role_and_employees list directly, to consolidate arguments?
	employeeRank = 100
	#TODO highest aptitude for role

	if isDouble(employee, schedule, role):
		employeeRank -=80
	if employee.shiftsRemaining(schedule) <= 2:
		employeeRank -= 40
	# print(employee.name)
	# print(employeeRank)

	return employeeRank


def createSchedule(roles, employees):
	week_schedule = []
	for role in roles:
		#find all the available employees for role
		possible_employees = [employee for employee in employees if can_take_on_role(employee, role, week_schedule)]
		#assign the best employee for the role
		try:
			role_and_employee = (role, max(possible_employees, key=lambda employee: employee_role_rank(employee, week_schedule, role) ))
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

# [(<__main__.Role object at 0x10877fb20>, <__main__.Employee object at 0x10877c7c0>)]

def scheduleView_Restaurant(schedule):
	'''print the schedule in 'Restaurant View' '''
	for i in range(7): # for the seven days of the week.
		headerDate= Weekday(i)
		print(f'{headerDate}')
		for grouping in schedule:
			role = grouping[0]
			employee = grouping[1]
			if role.day == headerDate:
				print(f'{role.name}: {employee.name}')

def scheduleView_SinglePerson(schedule, employee):
	'''print schedule for single person point of view '''
	pass

if __name__ == "__main__":
	weekly_schedule = createSchedule(roles, employees)

	scheduleView_Restaurant(weekly_schedule)