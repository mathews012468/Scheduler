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
    schedule = repairAvailability(schedule)
    schedule = repairPreferences(schedule)

    logger.debug(f"Remaining doubles: {identifyDoubles(schedule)}")
    
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
    
    #select staff with highest shifts remaining from possibleSwapPairs
    possibleSwapPairs.sort(key= lambda pair: pair[1].shiftsRemaining(schedule), reverse= True)
    swapPair = possibleSwapPairs[0]

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
    MAX_ATTEMPTS = 100
    attempts = 0
    while doubles != [] and attempts < MAX_ATTEMPTS:
        #if a double can't be repaired, this makes
        #sure that we can take care of another double
        #in the meantime. It's probably possible that
        #there will be some doubles that can't be resolved,
        #but hopefully that's unlikely. To take care of that
        #issue, I've added a max attempts that stops this
        #if it goes on too long.
        doubleToRepair = random.choice(doubles) #Question: why random choice over iterating through the list in order?
        schedule = repairDouble(schedule, doubleToRepair)
        doubles = identifyDoubles(schedule)

        attempts += 1
        if attempts == 99:
            logger.warning('Max Attempts reached')

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


def identifyUnavailablePairs(schedule):
    """
    Produce a list of pairs from the schedule
    where staff are paired with roles they are unavailable for
    """
    unAvailablePairs = []
    #for pair in schedule check if the role's calltime is in staff's availability.
    #if not, then append to list of unavailablePairs
    for role, staff in schedule:
        if not staff.isAvailable(role):
            unAvailablePairs.append((role,staff))
    return unAvailablePairs

def swapShifts(schedule, shift1, shift2):
    logger.info(f'swapping {shift1} with {shift2}')
    #1. swap staff of pairs
    newPair1 = (shift1[0], shift2[1])
    newPair2 = (shift2[0], shift1[1])
    logger.debug(f'swapped pairs created.')
    #2. add new pairs to schedule
    schedule.append(newPair1)
    logger.debug(f'added {newPair1}')
    schedule.append(newPair2)
    logger.debug(f'added {newPair2}')
    #3. remove old pairs from schedule
    schedule.remove(shift1)
    logger.debug(f'removed old pair {shift1}')
    schedule.remove(shift2)
    logger.debug(f'removed old pair {shift2}')
    logger.info('pairs swapped')
    return schedule


def repairUnavailable(unAvailablePair, schedule):
    repairRole = unAvailablePair[0]
    logger.debug(f'role to repair: {repairRole}')
    repairStaff = unAvailablePair[1]
    logger.debug(f'staff to repair: {repairStaff}')
    #get a list of available staff pairs
    availableStaffPairs = [pair for pair in schedule if pair[1].isAvailable(repairRole)]
    logger.debug(f'available staff pairs: {availableStaffPairs}')
    #get list of possible swap pairs
    possibleSwapPairs = [pair for pair in availableStaffPairs if repairStaff.isAvailable(pair[0])]
    logger.debug(f'possible swap pairs: {possibleSwapPairs}')
    if possibleSwapPairs == []:
        logger.warning(f'no swap pair for {unAvailablePair}')
        return schedule
    swapPair = random.choice(possibleSwapPairs)
    logger.debug(f'selected {swapPair} as target swap')
    schedule = swapShifts(schedule, unAvailablePair, swapPair)
    return schedule

def repairAvailability(schedule):
    'Repair roles with respect to staff availablity and nothing else'
    unAvailablePairs = identifyUnavailablePairs(schedule)
    logger.debug(f'BEFORE: number of unavailable pairs:{len(unAvailablePairs)}\n{unAvailablePairs}')
    
    MAX_ATTEMPTS = 100
    attempts = 0
    while unAvailablePairs != [] and attempts < MAX_ATTEMPTS:
        selectedPair = random.choice(unAvailablePairs)
        logger.debug(f'selected {selectedPair} to repair')
        schedule = repairUnavailable(selectedPair, schedule)
        unAvailablePairs = identifyUnavailablePairs(schedule)
        attempts += 1
        if attempts == 99:
            logger.warning('Max Attempts reached')
    unAvailablePairs = identifyUnavailablePairs(schedule)

    logger.debug(f'AFTER: number of unavailable pairs:{len(unAvailablePairs)}\n{unAvailablePairs}')
    return schedule


#There are two kinds of preference:
    #Role preference: staff which the Role preferres
    #Staff preference: roles which the staff preferres
def repairRolePreference(schedule):
    return schedule

def repairStaffPreference(schedule):
    return schedule
