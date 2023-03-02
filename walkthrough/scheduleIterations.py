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
    schedule = repairMaxShifts(schedule)
    schedule = repairAvailability(schedule)
    schedule = repairPreferences(schedule)

    logger.debug(f"Remaining doubles: {identifyDoubles(schedule)}")
    
    return schedule

def repairDouble(schedule, double):
    """
    Take in schedule, and the role-staff pair to reassign
    """
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

    return schedule

def repairDoubles(schedule):
    doubles = identifyDoubles(schedule)
    while doubles != []:
        schedule = repairDouble(schedule, doubles[0])
        doubles = identifyDoubles(schedule)

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

def repairMaxShifts(schedule):
    return schedule

def repairAvailability(schedule):
    return schedule

def repairPreferences(schedule):
    return schedule
