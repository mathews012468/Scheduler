# Roles made up of, name, weekday of role, callTime
# Staff is name, maxium shifts, and availability

# pass in variables, minimize messing with state.

# Goal:
# Take in a collection of roles
# Take in a collection of staff
# Return the collection of roles paired with appropriate staff 


# Strategy for selecting 'appropriate' staff:
# select the first role of the role collection.
# from the staff collection, get a pool of all staff who are available for the selected role's call time.
# order the pool of available staff with highest shifts remaining at the front.
# select the first staff from the ordered pool.
# pair selected staff with selected role.
	# UNLESS following conditons are true. This is where I am stuck on how to represent this.

# if selected staff is already scheduled for a shift on the selected role's weekday:
# 	place selected staff into a 'prefered last' pool
# 	select next staff from the Ordered Pool.

# if the Ordered Pool has been iterated through (no appropriate staff has been found):
# 	order the Prefered Last pool by highest shifts remaining at the front.
# 	select the first staff from Prefered Last.

# pair selected staff with selected role

# select next role from the role collection...repeat until all roles from the role collection have been paired with a member of the staff collection.
from enum import Enum
import datetime

class Weekdays(Enum):
	MODNAY = 'monday'
	TUESDAY = 'tuesday'
	WEDNESDAY = 'wednesday'
	THURSDAY = 'thursday'
	FRIDAY = 'friday'
	SATURDAY = 'saturday'
	SUNDAY = 'sunday'

class Role: #pasted in from main
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


	#roleCollection comes in, segmented into days? No, it does not need to be.
def pairAvailableStaff(roleCollection, staffColletion):
	roleStaffPairs = []
	for role in roleCollection: # select the first role of the role collection.
		availableStaff = [staff for staff in staffColletion if staff.isAvailable(role.callTime)] # from the staff collection, get a pool of all staff who are available for the selected role's call time.
		if availableStaff == []:
			raise RuntimeError(f'No staff available for {role}')
		availableStaff.sort(key = shiftsRemaining) # order the pool of available staff with highest shifts remaining at the front.
		staff = availableStaff[0] # select the first staff from the ordered pool.
		roleStaffPairs.append((role,staff)) #pair selected staff with selected role.
	return roleStaffPairs

	

		#now, the staff does not get paired when they meet one of the following exceptions.
		#in that case, the next staff gets picked from the list.

		#so, first we pick the first staff and check them against conditions of:
		#Is the staff already paired with a role that same weekday?

		#Another way to do it is to pair the role with the first staff of the available ordered list
		#and then in a second pass, check each role and staff pair, and see if there are any doubles that day.
		#When double is found, check for staff who is available and not scheduled that day.
		#Replace the staff pairing.
		#That is it's own sweep iteration.


def repairDoubles(roleStaffPairs):
	for weekday in Weekdays:
		weekdayPairs = [pair for pair in roleStaffPairs if pair[0].day == weekday]
		for pairs in weekdayPairs:
			staffIndecies = [index for index,staff in enumerate(weekdayPairs) if staff == pairs[1]]
			if len(staffIndecies) > 1:
				#repair double occurance
				#oh my god I need access to so much information to do this.
				#A list of who is working today
				#A list of who is available for this role, and is not working this day
				#I need to access the role of the staff first.
				#Aaaaaaaaaaaaa


		#find all occurances of a staff member appearing <1 times in this list of pairs.

	#get a list of all roleStaffPairs, whose role.weekday is == 'weekday'

		#To do this, get a collection of all the roleStaffPairs for a certain weekday.
		#To get this collection from the full week collection.
		# in roleStaffCollection:
		# find each pair from a certain weekday.

#This is the way to do it.
		#weekdays come with roles, a role is of a weekday.
		#when creating roleStaffPairs, the weekday seperation can be maintained.
		#for weekday in Weekdays:
			#for role in roleCollection.
				#weekdayRoles = [role for role in roleCollection if role.day == 'weekday']


		#For each multiple occurance of a staff in the roleStaffPairs.
			#Find a replacement staff who is not scheduled for a shift that day.

		#What are the excpetions of this sweep?
		# a double is found, and no replacement is found
		# raise error.

		#Then, once the double sweep has occured.
		#An aptitdue sweep can take place.
		# for each role/staff pair, is anyone paired into a role they are unsuited for?
		#find replacements for staff pairings with roles.

		#With each of these sweeps there are possible exceptions, how they are handeled, would be to the specfics of the sweep.
		#This aligns with the modular setup I am wanting.


		#Another way to phrase this is.
		#Select first staff from the order pool, and check them against a set of conditions
		#if all conditions are False, pair the selected staff with selected role.





		#UNLESS following conditons are true. This is where I am stuck on how to write this.
		# if selected staff is already scheduled for a shift on the selected role's weekday:
			# place selected staff into a 'prefered last' pool
			# select next staff from the Ordered Pool.

		#And then,
		# if the Ordered Pool has been iterated through (no appropriate staff has been found):
			# order the Prefered Last pool by highest shifts remaining at the front.
			# select the first staff from Prefered Last.

		#There is some basic grasp of loops or if statement flow that I am apparently not understanding.


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




def shiftsRemaining(staff, schedule):
	shiftCount = 0
	for staff in schedule:
		shiftCount += 1

	return staff.maxShifts - shiftCount