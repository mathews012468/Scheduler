import random
import logging
from classes import Weekdays

logger = logging.getLogger(__name__)

def startSchedule(roleCollection, staffCollection):
    """
    For each role, pick random employee with max shifts remaining
    """
    #generate dictionary where keys are shifts remaining
    #and values are list of employees with that number of shifts
    staffByShifts = {}
    for staff in staffCollection:
        shiftsRemaining = staff.maxShifts
        staffByShifts.setdefault(shiftsRemaining, [])
        staffByShifts[shiftsRemaining].append(staff)
    maxRemainingShifts = max(staffByShifts)

    #shuffle role collection
    roles = random.sample(roleCollection, k=len(roleCollection))
    schedule = []
    for role in roles:
        staff = random.choice(staffByShifts[maxRemainingShifts])
        #move staff to lower key, possibly remove key and update max
        #if that was the last staff with that number of shifts remaining
        staffByShifts[maxRemainingShifts].remove(staff)
        staffByShifts.setdefault(maxRemainingShifts-1, [])
        staffByShifts[maxRemainingShifts-1].append(staff)
        if staffByShifts[maxRemainingShifts] == []:
            del staffByShifts[maxRemainingShifts]
            maxRemainingShifts -= 1
        schedule.append((role,staff))
    logger.debug(staffByShifts)
    return schedule

def createSchedule(roleCollection, staffCollection):
    schedule = startSchedule(roleCollection, staffCollection)
    schedule = repairDoubles(schedule)
    schedule = repairUnavailables(schedule)
    schedule = repairPreferences(schedule)

    logger.debug(f"Remaining doubles: {identifyDoubles(schedule)}")
    unavailables = identifyUnavailables(schedule)
    logger.debug(f"Remaining unavailabilities: {unavailables}")
    logger.debug(f"Number of unavailables: {len(unavailables)}")
    
    return schedule

def repairDouble(schedule, double):
    """
    Take in schedule, and the role-staff pair to reassign
    """
    logger.info(f"Double to be resolved: {double}")
    dayOfDoubleShift = double[0].day
    staffWorkingDoubles = double[1]
    #find all staff not working on day of the role to be reassigned,
    #these are the possible swap partners
    allStaff = {pair[1] for pair in schedule}
    staffWorkingOnDoubleDay = {pair[1] for pair in schedule if pair[0].day is dayOfDoubleShift}
    possibleSwapPartners = allStaff - staffWorkingOnDoubleDay
    logger.debug(f"Possible swap partners: {possibleSwapPartners}")

    #find all days the staff member currently working the double shift 
    # is not currently working
    #these are the days we can reassign that staff
    allDays = {day for day in Weekdays}
    daysWhenDoubledStaffIsWorking = {pair[0].day for pair in schedule if pair[1] is staffWorkingDoubles}
    possibleSwapDays = allDays - daysWhenDoubledStaffIsWorking
    logger.debug(f"Possible swap days: {possibleSwapDays}")

    #get a list of all roles filled by the possible swap partners on the days
    #the staff member working the double shift is not working
    possibleSwapPairs = [pair for pair in schedule if pair[0].day in possibleSwapDays and pair[1] in possibleSwapPartners]

    if possibleSwapPairs == []:
        #no way to resolve this double (for now), so just return the current schedule as is
        logger.info(f"{double} cannot be resolved at the moment.")
        return schedule
    
    #pick a random role from that list as the swap
    swapPair = random.choice(possibleSwapPairs)

    #to make swap
    #1. remove pairs to be changed
    schedule.remove(double)
    schedule.remove(swapPair)
    #2. swap staff
    newPair1 = (double[0], swapPair[1])
    newPair2 = (swapPair[0], double[1])
    #3. add fixed pairs back to schedule
    schedule.append(newPair1)
    schedule.append(newPair2)

    logger.info(f"Double resolved: {double}")
    return schedule

def repairDoubles(schedule):
    doubles = identifyDoubles(schedule)
    logger.debug(f"Doubles to take care of: {doubles}")
    MAX_ATTEMPTS = 100
    attempts = 0
    #It's probably possible that there will be some doubles 
    # that can't be resolved, but hopefully that's unlikely. 
    # To take care of that issue, I've added a max attempts 
    # that stops this if it goes on too long.
    while doubles != [] and attempts < MAX_ATTEMPTS:
        #if a double can't be repaired, picking a random 
        # double to fix (instead of always picking the first, 
        # for example) allows us to take care of another double
        # in the meantime.
        doubleToRepair = random.choice(doubles)
        schedule = repairDouble(schedule, doubleToRepair)
        doubles = identifyDoubles(schedule)

        attempts += 1

    return schedule

def identifyDoubles(roleStaffPairs):
	"""
	take in current schedule, list of (role, staff)
	return list of staff that are doubled in a day in that list
	"""
	
	#if staff has already worked that day, then it's a double
	doubles = []
	staffDays = set() #set of staff day pairs
	for pair in roleStaffPairs:
		staff = pair[1]
		day = pair[0].day
		staffDay = (staff, day)

		if staffDay in staffDays:
			doubles.append(pair)
		else:
			staffDays.add(staffDay)
	return doubles

def repairUnavailables(schedule):
    unavailables = identifyUnavailables(schedule)
    logger.debug(f"Unavailables to fix: {unavailables}")
    logger.debug(f"Number of unavailables: {len(unavailables)}")

    MAX_ATTEMPTS = 100
    attempts = 0

    while unavailables != [] and attempts < MAX_ATTEMPTS:
        unavailableToRepair = random.choice(unavailables)
        schedule = repairUnavailable(schedule, unavailableToRepair)
        unavailables = identifyUnavailables(schedule)

        attempts += 1

    return schedule

def repairUnavailable(schedule, unavailableToRepair):
    logger.info(f"Unavailable pair to be resolved: {unavailableToRepair}")
    unavailableRole = unavailableToRepair[0]
    unavailableStaff = unavailableToRepair[1]

    #find all staff not working on day of unavailability 
    # and are available for the role to be repaired
    allStaff = {pair[1] for pair in schedule}
    staffWorkingThatDay = {pair[1] for pair in schedule if pair[0].day is unavailableRole.day}
    staffAvailableForRole = {pair[1] for pair in schedule if pair[1].isAvailable(unavailableRole)}
    possibleSwapPartners = (allStaff - staffWorkingThatDay) & staffAvailableForRole

    #find all days where unavailable staff isn't working
    allDays = {day for day in Weekdays}
    daysWhenUnavailableStaffIsWorking = {pair[0].day for pair in schedule if pair[1] is unavailableStaff}
    possibleSwapDays = allDays - daysWhenUnavailableStaffIsWorking

    #list of roles unavailable staff could work that are currently being staffed
    #by one of the possible swap partners
    possibleSwapPairs = [pair for pair in schedule if pair[0].day in possibleSwapDays and unavailableStaff.isAvailable(pair[0]) and pair[1] in possibleSwapPartners]
    logger.debug(f"Possible swap pairs (availability): {possibleSwapPairs}")

    if possibleSwapPairs == []:
        #no way to resolve this unavailability, so just return the schedule as is
        logger.info(f"{unavailableToRepair} cannot be resolved at the moment.")
        return schedule
    
    #pick a random role from that list as the swap
    swapPair = random.choice(possibleSwapPairs)

    #to make swap
    #1. remove pairs to be changed
    schedule.remove(unavailableToRepair)
    schedule.remove(swapPair)
    #2. swap staff
    newPair1 = (unavailableRole, swapPair[1])
    newPair2 = (swapPair[0], unavailableStaff)
    #3. add fixed pairs back to schedule
    schedule.append(newPair1)
    schedule.append(newPair2)

    logger.info(f"Unavailability resolved: {unavailableToRepair}")
    return schedule

def identifyUnavailables(schedule):
    """
    Return list of all role-staff pairs where the staff is
    unavailable to work the role
    """
    return [pair for pair in schedule if not pair[1].isAvailable(pair[0])]

def repairPreferences(schedule):
    return schedule
