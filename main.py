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
		
# May not be needed.
class Day:
	# The appeal of a Day object stems from wanting a container for a day's role names.
	# a space for a date is appealing too.
	def __init__(self, name, roles=None, date=None):
		self.name = name
		self.date = date #date object?

		# The idea is to have this list of role names exposed, editable as needed.
		roles = {
			Weekday.MONDAY: ['lunch', 'back', 'aux'],
			Weekday.TUESDAY: ['lunch']
		}
		self.roles = roles.get(name, roles)
		if self.roles is None:
			raise ValueError('Hey this is fucked')

class Role:
	def __init__(self, name, day=None, callTime=None, date=None): 
		self.name = name

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

#Current structure with two options:
#1) 'hardcoded' monday = [list of role names]
monday_list = ['lunch', 'back', 'aux']
tuesday_list = ['lunch']

#2) Day objects that get created 'somewhere':
monday = Day(name=Weekday.MONDAY)
tuesday = Day(name=Weekday.TUESDAY)

def compileWeek(): # A week contains whatever day objects have been created?
	pass

week = [monday,tuesday] # somehow we get here.

def createRoles(week):
	'''creates a list of Role objects based on roles named in a 'week' '''
	roles = []
	for day in week:
		for role_name in day.roles:
			role = Role(name=role_name, day=day.name)
			roles.append(role)
	return roles

#this version assigns the employee to the role object at role.employee.
#this came up since I was having trouble retrieving the data of each role,employee pair
#when trying to display it in the scheduleView functions below.
#though with this approach, the role objects get denser and denser as they go-
#This might have downsides I'm unaware off?

#Also- it doens't actually work cause the related functions, can_take_on_role and such
# have not be re-written to take in this approach.
def createSchedule_objectversion(week, employees):
	roles = createRoles(week)
	week_schedule = []
	for role in roles:
		possible_employees = [employee for employee in employees if can_take_on_role(employee, role, week_schedule)]
		#find possible employees who have matching availability
		try:
			role.employee = max(possible_employees, key=lambda employee: employee_role_rank(employee, week_schedule, role))
		except ValueError:
			role.employee = Employee('Unassigned',99,{})
		week_schedule.append(role)

	return week_schedule

def createSchedule(week_roles, employees):
	#roles = createRoles(week)
	week_schedule = []
	for role in week_roles:
		#find all the available employees for role
		possible_employees = [employee for employee in employees if can_take_on_role(employee, role, week_schedule)]
		#assign the best employee for the role
		try:
			role_and_employee = (role, max(possible_employees, key=lambda employee: employee_role_rank(employee, week_schedule, role) ))
		except ValueError:
			role_and_employee = (role, Employee('Unassinged',99,{}))
		week_schedule.append(role_and_employee)

	return week_schedule

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
	print(employee.name)
	employeeShifts = sorted([grouping[0] for grouping in schedule if employee in grouping], key=lambda role: role.day.value)
	for role in employeeShifts:
		print(f'{role.day.name.capitalize()}- {role.name.capitalize()} {role.callTime}')

if __name__ == "__main__":
	weekly_schedule = createSchedule(week, employees)

	#weekly_schedule = createSchedule_objectversion(week, employees)
	#print(weekly_schedule)

	scheduleView_Restaurant(weekly_schedule)
	# scheduleView_SinglePerson(weekly_schedule,employees[0])