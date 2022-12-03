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


def formSchedule_stuck(roleCollection, staffColletion):
	schedule = []
	for role in roleCollection: # select the first role of the role collection.
		availableStaff = [staff for staff in staffColletion if staff.isAvailable(role.callTime)] # from the staff collection, get a pool of all staff who are available for the selected role's call time.
		availableStaff.sort(key = shiftsRemaining) # order the pool of available staff with highest shifts remaining at the front.
		staff = availableStaff[0] # select the first staff from the ordered pool.

		#UNLESS following conditons are true. This is where I am stuck on how to write this...

		schedule.append((role,staff))


def formSchedule(roleCollection, staffCollection):
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