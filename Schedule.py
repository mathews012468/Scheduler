# Schedule is made up of:
# 	Collecetion of Roles
# 	Collection of Staff

# Roles made up of, name, weekday of role, callTime
# Staff is name, maxium shifts, and availability

# pass in variables when possible.
# minimize messing with state.


# Strategy:
# Take in a collection of roles
# Take in a collection of staff

# select the first role of the role collection.
# get the role's call time

# from the staff collection, get a pool of all staff who are available for the selected role's call time.
# order the pool of available staff with highest shifts remaining at the front.
# select the first staff from the ordered pool.

# 	if selected staff is already scheduled for a shift on this role's weekday:
# 		place selected staff into a 'prefered last' pool
# 		select next staff from the Ordered Pool.

# 	if the Ordered Pool has been iterated through once- is exhausted:
# 		order Prefered Last pool by highest shifts remaining at the front.
# 		select the first staff from Prefered Last.

# assign selected staff to role

# select next role from the role collection...repeat until all roles from the role collection have been paired with a member of the staff collection.

def formSchedule(roleCollection, staffCollection):
	schedule = []
	for role in roleCollection:
		availableStaff = [staff for staff in staffCollection if staff.isAvailable(role.callTime)]
		availableStaff.sort(key= shiftsRemaining())
		lowPriority = []

		for staff in availableStaff:
			if staff.isDouble():
				staff.append(lowPriority)
				continue
			else:
				schedule.append((role,staff))
				break
		lowPriority.sort(key = shiftsRemaining())
		schedule.append((role,lowPriority[0]))

	return schedule


def shiftsRemaining():
	pass