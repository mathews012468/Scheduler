import random
import logging
from classes import Weekdays
import copy

logger = logging.getLogger(__name__)

class Schedule:
    def __init__(self, roles, staff):
        self.roles = roles
        self.staff = staff
        self.schedule = self.startSchedule()

    def startSchedule(self):
        """
        For each role, pick random employee with max shifts remaining
        """
        #generate dictionary where keys are shifts remaining
        #and values are list of employees with that number of shifts
        staffByShifts = {}
        for staff in self.staff:
            #makes sure shifts remaining aligns with a staff's indicated availability
            shiftsRemaining = min(staff.maxShifts, numberOfDaysCouldWork(staff))
            logger.debug(f"Staff: {staff}, shifts remaining: {shiftsRemaining}, max shifts: {staff.maxShifts}, days could work: {numberOfDaysCouldWork(staff)}")
            staffByShifts.setdefault(shiftsRemaining, [])
            staffByShifts[shiftsRemaining].append(staff)
        maxRemainingShifts = max(staffByShifts)

        #shuffle role collection
        roles = random.sample(self.roles, k=len(self.roles))
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
    
    def repairDoubles(self):
        doubles = identifyDoubles(self.schedule)
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
            self.repairDouble(doubleToRepair)
            doubles = identifyDoubles(self.schedule)

            attempts += 1
        
    def repairDouble(self, double):
        """
        Take in schedule, and the role-staff pair to reassign
        """
        logger.info(f"Double to be resolved: {double}")
        dayOfDoubleShift = double[0].day
        staffWorkingDoubles = double[1]
        #find all staff not working on day of the role to be reassigned,
        #these are the possible swap partners
        allStaff = {pair[1] for pair in self.schedule}
        staffWorkingOnDoubleDay = {pair[1] for pair in self.schedule if pair[0].day is dayOfDoubleShift}
        possibleSwapPartners = allStaff - staffWorkingOnDoubleDay
        logger.debug(f"Possible swap partners: {possibleSwapPartners}")

        #find all days the staff member currently working the double shift 
        # is not currently working
        #these are the days we can reassign that staff
        allDays = {day for day in Weekdays}
        daysWhenDoubledStaffIsWorking = {pair[0].day for pair in self.schedule if pair[1] is staffWorkingDoubles}
        possibleSwapDays = allDays - daysWhenDoubledStaffIsWorking
        logger.debug(f"Possible swap days: {possibleSwapDays}")

        #get a list of all roles filled by the possible swap partners on the days
        #the staff member working the double shift is not working
        possibleSwapPairs = [pair for pair in self.schedule if pair[0].day in possibleSwapDays and pair[1] in possibleSwapPartners]

        if possibleSwapPairs == []:
            #no way to resolve this double (for now), so do nothing with the schedule
            logger.info(f"{double} cannot be resolved at the moment.")
            return
        
        #pick a random role from that list as the swap
        swapPair = random.choice(possibleSwapPairs)

        #to make swap
        #1. remove pairs to be changed
        self.schedule.remove(double)
        self.schedule.remove(swapPair)
        #2. swap staff
        newPair1 = (double[0], swapPair[1])
        newPair2 = (swapPair[0], double[1])
        #3. add fixed pairs back to schedule
        self.schedule.append(newPair1)
        self.schedule.append(newPair2)

        logger.info(f"Double resolved: {double}")

def numberOfDaysCouldWork(staff):
    days = 0
    for times in staff.availability.values():
        if times != []:
            days += 1
    return days

def createSchedule(roleCollection, staffCollection):
    schedule = Schedule(roles=roleCollection, staff=staffCollection)
    schedule.repairDoubles()

    schedule = schedule.schedule
    
    logger.debug(f"Remaining doubles: {identifyDoubles(schedule)}")
    unavailables = identifyUnavailables(schedule)
    logger.debug(f"Remaining unavailabilities: {unavailables}")
    logger.debug(f"Number of unavailables: {len(unavailables)}")
    schedule = repairUnavailables(schedule)
    schedule = repairPreferences(schedule)

    beforeUnavailables = len(unavailables)
    logger.debug(f"Remaining doubles: {identifyDoubles(schedule)}")
    unavailables = identifyUnavailables(schedule)
    logger.debug(f"Remaining unavailabilities: {unavailables}")
    logger.debug(f"Number of unavailables: {len(unavailables)}")
    logger.debug(f"Unavailables removed: {beforeUnavailables - len(unavailables)}")
    
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

def couldWorkRole(staff, role, schedule):
    allDays = {day for day in Weekdays}
    staffWorkingDays = {pair[0].day for pair in schedule if pair[1] is staff}
    possibleSwapDays = allDays - staffWorkingDays
    staffAlreadyWorksRole = False
    for pair in schedule:
        if pair[1] is staff and pair[0] is role:
            staffAlreadyWorksRole = True
            break

    return (role.day in possibleSwapDays or staffAlreadyWorksRole) and staff.isAvailable(role)

def repairUnavailables(schedule):
    unavailables = identifyUnavailables(schedule)
    
    MAX_ATTEMPTS = 100
    attempts = 0
    while unavailables != [] and attempts < MAX_ATTEMPTS:
        indexOfUnavailableToRepair = random.choice(unavailables)
        schedule = repairUnavailable(schedule, indexOfUnavailableToRepair)
        unavailables = identifyUnavailables(schedule)

        attempts += 1
        logger.debug(f"attempts: {attempts}")

    logger.debug(f"Unavailables: {unavailables}")
    return schedule

def repairUnavailable(schedule, indexOfUnavailableToRepair):
    """
    The staff at schedule[indexOfUnavailableToRepair] should not be available to work the current role
    they're assigned to. This function performs a series of swaps within the schedule fix this unavailability.
    Return the fixed schedule.
    """

    """
    We need to cap the maximum cycle length we look for because this could take a LONG time with a larger number.
    Try to change this to 8 to see how long it takes! (You might be able to get away with 5 or 6, just remember
    the point of this is to give us a wider range of options for fixing the schedule)
    """
    MAX_LENGTH = 4
    for length in range(2,MAX_LENGTH):
        allCycles = allCyclesOfLength(schedule, indexOfUnavailableToRepair, length)
        logger.debug(f"allCycles: {allCycles}")
        if allCycles == []:
            length += 1
            continue

        cycle = random.choice(allCycles)
        logger.debug(f"Repairing: {schedule[indexOfUnavailableToRepair]}, Cycle: {cycle}, Cycle with info: {[schedule[i] for i in cycle]}")
        schedule = cycleSwap(schedule, cycle)
        logger.debug(f"Doubles: {identifyDoubles(schedule)}")
        break

    return schedule

def cycleSwap(schedule, cycle):
    """
    Perform the sequence of swaps indicated by the cycle
    If cycle is [4, 10, 3], 4->10, 10->3, 3->4
    It turns out that every cycle can be broken down into direct swaps (official term is transposition).
    There's more than one way to do this, but the way it's being done in this function is to swap the
    first with the second, the first with the third, the first with the fourth, and so on, and that ends
    up performing the cycle we want.

    There's some math here, basically we're just using the identity mentioned in this stack exchange post: https://math.stackexchange.com/q/3358722
    For more info you can look up "decomposing cycles as a product of transpositions" or take a look at the lecture
    notes mentioned in that post.
    """
    for i in range(1,len(cycle)):
        logger.debug(f"Before swap in cycle swap. indices: {cycle[0]}, {cycle[i]}; info: {schedule[cycle[0]]}, {schedule[cycle[i]]}")
        pair1 = schedule[cycle[0]]
        pair2 = schedule[cycle[i]]
        newPair1 = (pair1[0], pair2[1])
        newPair2 = (pair2[0], pair1[1])

        schedule.remove(pair1)
        schedule.insert(cycle[0], newPair1)

        schedule.remove(pair2)
        schedule.insert(cycle[1], newPair2)
        logger.debug(f"After swap in cycle swap. indices: {cycle[0]}, {cycle[i]}; info: {schedule[cycle[0]]}, {schedule[cycle[i]]}")
    return schedule

def allCyclesOfLength(schedule, indexOfUnavailableToRepair, length):
    """
    Find all groups of role-staff pairs in 'schedule' of size 'length' involving the pair at index 'indexOfUnavailableToRepair'
    where the staff can be shuffled around while respecting doubles and availability.

    For example, if we're trying to find a group of size 3, we want to find three role-staff pairs where
    staff1 could work role2, staff2 could work role3, and staff3 could work role1.

    This is like a wrapper around the 'allCyclesOfLengthHelper' function to avoid setting up the graph, path, and visited lists
    in the 'repairUnavailable' function.

    Return list[list of indices of the pairs in the schedule forming the cycle]
    """

    """
    graph is an adjacency matrix, it describes which role-staff pairs are connected to other role-staff pairs
    graph is an array of arrays, where each array's length is the number of pairs in the schedule
    The element at row i and column j is True if the staff of pair i could work the role of pair j,
    i.e. it's saying that staff i could be reassigned to role j without breaking doubles/availability
    """
    graph = [[couldWorkRole(pair2[1], pair1[0], schedule) for pair1 in schedule] for pair2 in schedule]

    path = [indexOfUnavailableToRepair]
    #at the start, nothing but the node we're repairing has been visited, 
    # since the cycle we're looking for should start with that node
    visited = [False for i in range(len(schedule))]
    visited[indexOfUnavailableToRepair] = True

    return allCyclesOfLengthHelper(graph, length, path, visited)
    
def allCyclesOfLengthHelper(graph, length, path, visited):
    """
    Find all paths of length 'length' in 'graph' building off of path 
    and ending at the start of path (which makes a cycle). 
    Graph is a list of lists, is an adjacency matrix. 
    Path is a list of the elements in the path so far (list[int])
    Length is an int representing how many more nodes we need to walk along in the path
    visited is a list of bools letting us know which nodes have been visited (so we don't visit them again)

    Return a list[list[int]]
    """
    cycles = []
    currentNode = path[-1]
    if length == 1:
        startNode = path[0]
        #only add path to cycles if the current node connects to the start node
        if graph[currentNode][startNode]:
            cycles.append(path)
        return cycles
    
    unvisitedNeighbors = [index for index, (isNeighbor, didVisit) in enumerate(zip(graph[currentNode], visited)) if isNeighbor and not didVisit]
    logger.debug(f"length: {length}, path: {path}, visited: {visited}, unvisitedNeighbors: {unvisitedNeighbors}")
    for neighbor in unvisitedNeighbors:
        newVisited = copy.deepcopy(visited)
        newVisited[neighbor] = True
        newCycles = allCyclesOfLengthHelper(graph, length-1, path + [neighbor], newVisited)
        logger.debug(f"neighbor: {neighbor}, newCycles: {newCycles}")
        cycles.extend(newCycles)
    return cycles

def identifyUnavailables(schedule):
    """
    Return list of all role-staff pairs where the staff is
    unavailable to work the role
    """
    return [i for i, pair in enumerate(schedule) if not pair[1].isAvailable(pair[0])]

def repairPreferences(schedule):
    return schedule
