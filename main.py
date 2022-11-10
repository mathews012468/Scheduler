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
			raise ValueError(f'Provide recognized role name or call time. Provided: {name} {callTime}')


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

	return employeeRank


def createRoles(week):
	'''creates a list of Role objects based on roles named in a 'week' '''
	rolesOfWeek = []
	for day in week:
		for dayName,roles in day.items():
			rolesOfDay = [Role(name=roleName, day=dayName) for roleName in roles]
		rolesOfWeek.append(rolesOfDay)
	return rolesOfWeek


def createSchedule(rolesOfWeek, employees):
	week_schedule = []
	for day in range(len(rolesOfWeek)):
		for role in rolesOfWeek[day]:
			#find all the available employees for role
			possible_employees = [employee for employee in employees if can_take_on_role(employee, role, week_schedule)]
			#assign the best employee for the role
			try:
				role_and_employee = (role, max(possible_employees, key=lambda employee: employee_role_rank(employee, week_schedule, role) ))
			except ValueError:
				role_and_employee = (role, Employee('Unassinged',99,{}))
			week_schedule.append(role_and_employee)

	return week_schedule


def scheduleView_Restaurant(schedule, week):
	'''print the schedule in 'Restaurant View' '''
	for day in range(len(week)): # for the seven days of the week.
		headerDate= Weekday(day)
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