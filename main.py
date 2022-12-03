import random, datetime, os
from enum import Enum

class Weekday(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

#For the moment, this seems like using a class as a module, avoiding a circular import. 
class ProcessInput:
    """Contains functions to compile roles and compile staff from input.txt files"""

    def compileStaff(staffFileName):
        """compile staff from .txt file containing staff data"""
        staffFilePath = os.path.join('input', staffFileName)
        with open(staffFilePath) as f:
            weekStaff = []
            while line := f.readline():

                if line.lower().startswith('name'):
                    name = line.split(':')[1].strip()

                    line = f.readline() # move to shift line
                    maxShifts = line.split(':')[1].strip()

                    line = f.readline() # move to request line
                    requestLines = []
                    while True: #store the next set of lines
                        line = f.readline()
                        if line.startswith('\n'):
                            break
                        requestLines.append(line.strip())
                    availability = ProcessInput.setAvailability(requestLines) 

                    staffObject = Staff(name, int(maxShifts), availability)
                    weekStaff.append(staffObject)

            return weekStaff

    def setAvailability(requestLines):
        """set availability from staff request lines
        input: list of stripped request lines from staff .txt file
        returns: dictionary for Staff object availabiltiy
        """
        availability = {
                Weekday.MONDAY: [datetime.time(hour=8),datetime.time(hour=23)],
                Weekday.TUESDAY: [datetime.time(hour=8),datetime.time(hour=23)],
                Weekday.WEDNESDAY: [datetime.time(hour=8),datetime.time(hour=23)],
                Weekday.THURSDAY: [datetime.time(hour=8),datetime.time(hour=23)],
                Weekday.FRIDAY: [datetime.time(hour=8),datetime.time(hour=23)],
                Weekday.SATURDAY: [datetime.time(hour=8),datetime.time(hour=23)],
                Weekday.SUNDAY: [datetime.time(hour=8),datetime.time(hour=23)]
                }

        for line in requestLines:
            weekday, requestTimes = line.split(':')
            requestTimes = [hours for hours in requestTimes.split(',')]
            availability[Weekday[weekday.upper()]] =[] # clear weekday's default availability

            while requestTimes != []:
                start, end = requestTimes[:2]
                del requestTimes[:2]
                startHour, startMinute = start.split('.')
                endHour, endMinute = end.split('.')

                availability[Weekday[weekday.upper()]].append(datetime.time(int(startHour),int(startMinute) ) )
                availability[Weekday[weekday.upper()]].append(datetime.time(int(endHour),int(endMinute) ) )

        return availability

    def compileRoles(roleFileName):
        """input: .txt file containing names of roles and associated weekday
        Output: A list of dictionaries for each weekday.
        Dictionary[key] = Weekday.Enum
        Dictionary[value] = list of role names
        """
        roleFilePath = os.path.join('input', roleFileName)
        weekRoleNames=[]
        with open(roleFilePath) as file:
            while line := file.readline():
                if line == '\n' or line.startswith('#'): #ignore empty and #comment lines
                    continue
                day = Weekday[line.upper().strip()]

                line = file.readline()
                roles = [role.strip() for role in line.split(',')]

                weekRoleNames.append({day: roles})
        #create list of Role objects from weekRoleNames
        return ProcessInput.createRoles(weekRoleNames)

    def createRoles(compiledRoles):
        """Create Role Objects from compiled roles.txt input
        Input: List of dictionaries from compileWeek()
        Output: A list of lists containing Role Objects for each weekday
        """
        rolesOfWeek = []
        for dict in compiledRoles:
            for weekday,roles in dict.items():
                rolesOfDay = [Role(name=roleName, day=weekday) for roleName in roles]
            rolesOfWeek.append(rolesOfDay)
        return rolesOfWeek


#Writing out thought...

#I don't think I understand a 'schedule object'.
#The way I'm thinking about it now is a schedule can be a list of days.
#Each day containing...what?
#   The roles to be filled for a day.
#   The roles to be filled + staff available that day? That seems to be too much.
    
#to be specfic, here's the idea of a 'day'. A dictionary where key=WeekdayEnum, and value=[list of roles]
#This is what is created from txt input with the compileRoles function.

#Now, the next step, on how to proceed these 'day dictionaries' is where I start to get uncertain.
#CompileRoles gives me a list of dictionaries- a list of 'days'.
#then CreateRoles takes each dictionary, and creates a list of Role Objects.
#Since Role Objects have an attribute space for name, day, (and callTime).
#the dictionary collection is thrown out and the Role Objects are stored in an individual list.
#Now each 'day' is a list...

#That's frusterating becuase I'm unncertain of which direction to pick. A dictionary with redundent data-   
#Key=WeekdayEnum, Value=[list of Role Objects] WeekdayEnum is now redundant as a Key and Attribute of the Role Objects.
#Or
#A list of Role Objects. No more dict Key, and now a day can be retrieved with list index. [0] is the first day, [1] is the second...etc
#The annoyance here is the density of a list of lists. Which quickly amounts to retreiving data like this:

    """print(schedule.week) # a 'week'. Alist of lists of Role,Staff tuple pairs
    print(schedule.week[0]) # first 'day' of the week. List of Role,Staff tuple pairs
    print(schedule.week[0][0]) # first Role,Staff tuple pair of the first day
    print(schedule.week[0][0][1])# Staff object of the first Role,Staff object pair."""

#I'm now thinking that I'm using collections to store stuff too quickly in the process
#and that there's probably a way to achieve 'simple data retrieval' from objects themselves, rather than colletions inside collections.

#This idea of 'simple data retreivel' is something I'm interested in as I'm thinking it will keep me inline with this 'modular' and 'overseeable' way of working that I'm wanting.


#There's an instinctive annoyance with that kind of 'notation'. It feels unweildy and 'frusterating'.
#That is what I'm wanting to 'solve'.

#So what do I want?
#What would be 'smooth'? Is this about retreving data that is stored in a collection?
#I want 'simple retreival' Is that what I'm after?
#Yes. How do I set that up?

#This is works, as in the labels (name, weekday) and callTime data are available to use in functions like isAvailable.
#However, the resulting 'schedule' that is now a list of lists feels dense, and gets denser (i.e. more frusterating) with each element added to it from this point on.

#At this point the 'schedule' is made up of a list of lists of Role Objects. And now Staff Objects are introduced...
#Staff Objects are constructed from input, currently a txt file, and each Staff Object has an attirbute for a name.
#New attributes come up as ideas for 'creating the schedule' come forward, and currently there is:
#   Availabiltiy: a dictionary of time intervals. Key=weekday, Value=[list of timestamps]
#   MaxShifts: an int value
#   Soon to be: Aptitude or Preference, a collection of aptitudes or preferences for certain roles
#The desire is to add on any attribute as ideas come up.
#Why does that currently feel hard to do?

#A schedule as an object, can this help with that?
#A schedule as an object is an instance of a Schedule class. And this class object takes the form of a dict.
#Then the schedule class would look something like this:

#What does that mean? Now a schedule object is always a dictionary?
class Schedule_2(list):
    pass

#This quickly starts to seem redundent when Role objects currently have a weekd
class Schedule:
    def __init__(self, roleInput, staffInput, week=None):
        """"Create schedule object from role and staff inputs
        roleInput = string filename.txt
        staffInput = string filename.txt """
        #Right now these ProcessInput functions create the input that is used to build the schedule's week.
        #chainging the .txt filename input seems to say there is a 'better' solution.
        scheduleRoles = ProcessInput.compileRoles(roleInput)
        scheduleStaff = ProcessInput.compileStaff(staffInput)

        week = []
        for day in scheduleRoles:
            daySchedule = []
            for role in day:
                availableStaff = [staff for staff in scheduleStaff if isAvailable(role, staff)]
                roleStaffPair = (role, random.choice(availableStaff))
                daySchedule.append(roleStaffPair)
            week.append(daySchedule)

        self.week = week

#I don't see a situation where Staff and Role objects would want to 'talk to eachother'
#What possibilities open up with Staff and Role class moving inside of the Schedule class?

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


class Staff:
    def __init__(self, name, maxShifts, availability):
        self.name = name
        self.maxShifts = maxShifts
        self.availability = availability
        

def shiftsRemaining(staff, schedule):
    shiftsRemaining = staff.maxShifts
    flatSchedule = [pairs for day in schedule.week for pairs in day]
    shiftCount = 0
    for roleStaffPair in flatSchedule:
        if roleStaffPair[1] == staff:
            shiftsRemaining -= 1
    if shiftsRemaining < 0:
        raise ValueError(f'{staff.name} shiftsRemaing: {shiftsRemaining}')
    return shiftsRemaining


def isAvailable(role, staff):
    """check if role.callTime is in staff.availability"""
    day = role.day
    staffAvail = staff.availability[day]
    for i in range(0, len(staffAvail), 2): # iterate over staffAvail in 'chunks' of 2.
        availPair = staffAvail[i:i+2]
        startTime = availPair[0]
        endTime = availPair[1]
        if role.callTime >= startTime and role.callTime <= endTime:
            return True
        else:
            continue
    return False


def createWeekSchedule(rolesOfWeek, staffList):
    """Pair a member of staff with each role in a weekday of Roles
    input: list of Role objects from createRoles() and a list of Staff Objects
    output: a list of lists containing tuples of (RoleObject, StaffObject) pairs for each weekday
    """
    global weekSchedule # global for other functions to access.
    weekSchedule = []
    for day in rolesOfWeek:
        daySchedule = []
        for role in day:
            availableStaff = [staff for staff in staffList if isAvailable(role, staff)]
            roleStaffPair = (role, random.choice(availableStaff))
            daySchedule.append(roleStaffPair)
        weekSchedule.append(daySchedule)
    return weekSchedule



def scheduleView(schedule):
    """print schedule to screen"""
    for day in schedule:
        headerDate = day[0][0].day #day of first Role object
        print(f'---{headerDate}---')
        for roleStaffPair in day:
            role = roleStaffPair[0]
            staff = roleStaffPair[1]
            print(f'{role.name}: {staff.name}')



schedule = Schedule('roles_sixShifts.txt','staff_single.txt')
print(schedule.week) # a 'week'. Alist of lists of Role,Staff tuple pairs
print(schedule.week[0]) # first 'day' of the week. List of Role,Staff tuple pairs
print(schedule.week[0][0]) # first Role,Staff tuple pair of the first day
print(schedule.week[0][0][1])# Staff object of the first Role,Staff object pair.

#Does having the Role and Staff objects be part of the Schedule class
#allow for a different way to store the a week schedule?

