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

def identifyDoubles(roleStaffPairs):
	"""
	take in current schedule, list of (role, staff)
	return list of indices of staff that are doubled in a day in that list
	"""
	
	#if staff has already worked that day, then it's a double
	doubleIndices = []
	staffDays = set() #set of staff day pairs
	for index, pair in enumerate(roleStaffPairs):
		staff = pair[1]
		day = pair[0].day
		staffDay = (staff, day)

		if staffDay in staffDays:
			doubleIndices.append(index)
		else:
			staffDays.add(staffDay)
	return doubleIndices

def createSchedule(roleCollection, staffCollection):
    schedule = startSchedule(roleCollection, staffCollection)
    for index in identifyDoubles(schedule):
        logger.debug(f'before: {(index, schedule[index])}')
    schedule = repairDoubles(schedule)
    if identifyDoubles(schedule) == []:
        logger.debug(f'No Doubles!')
    else:
        for index in identifyDoubles(schedule):
            logger.debug(f'after: {(index, schedule[index])}')
    

    schedule = repairMaxShifts(schedule)
    schedule = repairAvailability(schedule)
    schedule = repairPreferences(schedule)
    return schedule

def repairDoubles(schedule):
    doublesIndices = identifyDoubles(schedule)
    logger.debug([schedule[index] for index in doublesIndices])
    for doubleIndex in doublesIndices:
        swapDouble(schedule, doubleIndex)
        afterSwapIndices = identifyDoubles(schedule)
        if doubleIndex in afterSwapIndices:
            logger.debug('hold up')

    return schedule

#to find staff who 
#a list of staff who is does not have role.day in their set of shifts
#a list of shifts per staff
#then get a list of staff who don't have role.day in their list of shifts
#a dictionary key.setdefault(staff.name)
#dict[staff.name].add(role)

def getStaffNotWorking(schedule, doubleRole):
    RolesPerStaff = {}
    notWorkingStaff = []
    workingDay = doubleRole.day
    for role, staff in schedule:
        RolesPerStaff.setdefault(staff,[])
        RolesPerStaff[staff].append(role.day)
    for staff in RolesPerStaff:
        if workingDay not in RolesPerStaff[staff]:
            notWorkingStaff.append(staff)
    logger.debug(f'staff not working on {doubleRole.day}: {notWorkingStaff}')
    return notWorkingStaff


def getDaysNotWorking(schedule, staff):
    daysNotWorking = []
    daysWorking = set()
    for pair in schedule:
        if pair[1] == staff:
            daysWorking.add(pair[0].day)
    for day in Weekdays:
        if day not in daysWorking:
            daysNotWorking.append(day)
    logger.debug(f'Double Staff: daysNotWorking:{daysNotWorking}')
    return daysNotWorking

def getPossibleSwaps(schedule, daysNotWorking, staffNotWorking):
    possibleSwaps = []
    for index, pair in enumerate(schedule):
        if pair[0].day in daysNotWorking and pair[1] in staffNotWorking:
            possibleSwaps.append((index,pair))
    return possibleSwaps


def swapDouble(schedule, doubleIndex):
    double = schedule[doubleIndex]
    #assigned role/staff
    doubleRole = double[0]
    doubleStaff = double[1]

    #get a list of all staff from the schedule not working on assigned staff's role.day.
    staffNotWorking = getStaffNotWorking(schedule, doubleRole)

    #for assigned staff get days not working
    daysNotWorking = getDaysNotWorking(schedule, doubleStaff)

    possibleSwaps = getPossibleSwaps(schedule, daysNotWorking, staffNotWorking)
    #sort possible swaps by staff's shifts remaining- highest at front.
    possibleSwaps.sort(key= lambda pair: pair[1][1].shiftsRemaining(schedule), reverse= True)
    swapIndex, swapShift= possibleSwaps[0] #(index,staff) tuple
    swapRole, swapStaff = swapShift

    schedule[doubleIndex] = (doubleRole, swapStaff)
    logger.debug(f'double index:{doubleIndex}')
    logger.debug(f'doubleStaff: {doubleStaff}')
    logger.debug(f'doubleRole: {doubleRole}')
    schedule[swapIndex] = (swapRole, doubleStaff)
    logger.debug(f'swap Index: {swapIndex}')
    logger.debug(f'swapStaff: {swapStaff}')
    logger.debug(f'swapRole: {swapRole}')
    
    return schedule

def repairMaxShifts(schedule):
    return schedule

def repairAvailability(schedule):
    return schedule

def repairPreferences(schedule):
    return schedule
