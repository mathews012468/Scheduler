import random
import logging
from classes import Weekdays
import copy

logger = logging.getLogger(__name__)

class Schedule:
    def __init__(self, roles, staff):
        self.roles = roles
        self.staff = staff
        #change schedule to a dict, role: staff
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
        schedule = {}
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
            schedule[role] = staff
        logger.debug(staffByShifts)
        return schedule
    
    def repairDoubles(self):
        doubles = self.identifyDoubles()
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
            doubles = self.identifyDoubles()

            attempts += 1
        
    def repairDouble(self, double):
        """
        Take in schedule, and the role to reassign
        """
        logger.info(f"Double to be resolved: {double}")
        dayOfDoubleShift = double.day
        staffWorkingDoubles = self.schedule[double]
        #find all staff not working on day of the role to be reassigned,
        #these are the possible swap partners
        allStaff = set(self.schedule.values())
        staffWorkingOnDoubleDay = {staff for role, staff in self.schedule.items() if role.day is dayOfDoubleShift}
        possibleSwapPartners = allStaff - staffWorkingOnDoubleDay
        logger.debug(f"Possible swap partners: {possibleSwapPartners}")

        #find all days the staff member currently working the double shift 
        # is not currently working
        #these are the days we can reassign that staff
        allDays = {day for day in Weekdays}
        daysWhenDoubledStaffIsWorking = {role.day for role, staff in self.schedule.items() if staff is staffWorkingDoubles}
        possibleSwapDays = allDays - daysWhenDoubledStaffIsWorking
        logger.debug(f"Possible swap days: {possibleSwapDays}")

        #get a list of all roles filled by the possible swap partners on the days
        #the staff member working the double shift is not working
        possibleSwapRoles = [role for role, staff in self.schedule.items() if role.day in possibleSwapDays and staff in possibleSwapPartners]

        if possibleSwapRoles == []:
            #no way to resolve this double (for now), so do nothing with the schedule
            logger.info(f"{double} cannot be resolved at the moment.")
            return
        
        #pick a random role from that list as the swap
        swapRole = random.choice(possibleSwapRoles)
        self.swap(double, swapRole)

        logger.info(f"Double resolved: {double}")

    def swap(self, role1, role2):
        self.schedule[role2], self.schedule[role1] = self.schedule[role1], self.schedule[role2]
        try:
            self.graph
        except AttributeError:
            return
        self.graph[role2], self.graph[role1] = self.graph[role1], self.graph[role2]
        for role in self.graph:
            self.graph[role][role2], self.graph[role][role1] = self.graph[role][role1], self.graph[role][role2]


    def tupleRepresentation(self):
        return [(role,staff) for role, staff in self.schedule.items()]
    
    def identifyDoubles(self):
        """
        return list of roles that need to be reassigned to avoid doubles
        """
        
        #if staff has already worked that day, then it's a double
        doubles = []
        staffDays = set() #set of staff day pairs
        for role, staff in self.schedule.items():
            day = role.day
            staffDay = (staff, day)

            if staffDay in staffDays:
                doubles.append(role)
            else:
                staffDays.add(staffDay)
        return doubles

    def repairUnavailables(self):
        unavailables = self.identifyUnavailables()
        
        MAX_ATTEMPTS = 500
        attempts = 0
        while unavailables != [] and attempts < MAX_ATTEMPTS:
            unavailableRole = random.choice(unavailables)
            self.repairUnavailable(unavailableRole)
            unavailables = self.identifyUnavailables()

            attempts += 1
            logger.debug(f"attempts: {attempts}")

        logger.debug(f"Unavailables: {unavailables}")

    def repairUnavailable(self, unavailableRole):
        """
        The staff at schedule[unavailableRole] should not be available to work the current role
        they're assigned to. This function performs a series of swaps within the schedule fix this unavailability.
        """

        """
        We need to cap the maximum cycle length we look for because this could take a LONG time with a larger number.
        Try to change this to 8 to see how long it takes! (You might be able to get away with 5 or 6, just remember
        the point of this is to give us a wider range of options for fixing the schedule)
        """
        logger.info(f"Unavailable role to fix: {unavailableRole}")
        MAX_LENGTH = 5
        for length in range(2,MAX_LENGTH):
            allCycles = self.allCyclesOfLength(unavailableRole, length)
            logger.debug(f"allCycles: {allCycles}")
            if allCycles == []:
                length += 1
                continue

            cycle = random.choice(allCycles)
            logger.debug(f"Repairing: {unavailableRole}-{self.schedule[unavailableRole]}, Cycle: {[(role, self.schedule[role]) for role in cycle]}")
            schedule = self.cycleSwap(cycle)
            # logger.debug(f"Doubles: {self.identifyDoubles()}")
            return
        
        logger.info(f"Currently no way of repairing {unavailableRole}")

    def cycleSwap(self, cycle):
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
            logger.debug(f"Before swap in cycle swap. indices: {cycle[0]}, {cycle[i]}; info: {self.schedule[cycle[0]]}, {self.schedule[cycle[i]]}")
            self.swap(cycle[0], cycle[i])
            logger.debug(f"After swap in cycle swap. indices: {cycle[0]}, {cycle[i]}; info: {self.schedule[cycle[0]]}, {self.schedule[cycle[i]]}")

    def allCyclesOfLength(self, unavailableRole, length):
        """
        Find all groups of roles in the schedule of size 'length' involving the 'unavailableRole'
        where the staff can be shuffled around while respecting doubles and availability.

        For example, if we're trying to find a group of size 3, we want to find three roles where
        staff1 could work role2, staff2 could work role3, and staff3 could work role1.

        This is like a wrapper around the 'allCyclesOfLengthHelper' function to avoid setting up the graph, path, and visited lists
        in the 'repairUnavailable' function.

        Return list[list of roles in the schedule forming the cycle]
        """

        """
        graph is an adjacency matrix, it describes which role-staff pairs are connected to other role-staff pairs
        graph is an array of arrays, where each array's length is the number of pairs in the schedule
        The element at row i and column j is True if the staff of pair i could work the role of pair j,
        i.e. it's saying that staff i could be reassigned to role j without breaking doubles/availability
        """
        #only do this once
        try:
            self.graph
        except AttributeError:
            self.graph = {role1: {role2: self.couldWorkRole(staff1, role2) for role2 in self.schedule} for role1, staff1 in self.schedule.items()}

        path = [unavailableRole]
        #at the start, nothing but the node we're repairing has been visited, 
        # since the cycle we're looking for should start with that node
        visited = {role: False for role in self.graph}
        visited[unavailableRole] = True

        return self.allCyclesOfLengthHelper(length, path, visited)
        
    def allCyclesOfLengthHelper(self, length, path, visited):
        """
        Find all paths of length 'length' in 'graph' building off of path 
        and ending at the start of path (which makes a cycle). 
        Graph is a list of lists, is an adjacency matrix. 
        Path is a list of the elements in the path so far (list[int])
        Length is an int representing how many more nodes we need to walk along in the path
        visited is a list of bools letting us know which nodes have been visited (so we don't visit them again)

        Return a list[list[int]]
        """
        logger.debug(f"start of allCyclesOfLengthHelper. length: {length}, path: {path}")
        cycles = []
        currentNode = path[-1]
        if length == 1:
            startNode = path[0]
            #only add path to cycles if the current node connects to the start node
            if self.graph[currentNode][startNode]:
                cycles.append(path)
            return cycles
        
        unvisitedNeighbors = [role for role in visited if self.graph[currentNode][role] and not visited[role]]
        logger.debug(f"length: {length}, path: {path}, unvisitedNeighbors: {unvisitedNeighbors}")
        for neighbor in unvisitedNeighbors:
            #can't do a deepcopy of visited because that changes the identity of the roles,
            #which is currently being used as the hash
            newVisited = {role: didVisit for role, didVisit in visited.items()}
            newVisited[neighbor] = True
            logger.debug(f"currentNode: {currentNode}, neighbor: {neighbor}")
            newCycles = self.allCyclesOfLengthHelper(length-1, path + [neighbor], newVisited)
            logger.debug(f"neighbor: {neighbor}, newCycles: {newCycles}")
            cycles.extend(newCycles)
        return cycles
        
    def identifyUnavailables(self):
        """
        Return list of all roles where the staff is
        unavailable to work the role
        """
        return [role for role, staff in self.schedule.items() if not staff.isAvailable(role)]

    def couldWorkRole(self, testStaff, testRole):
        allDays = {day for day in Weekdays}
        staffWorkingDays = {role.day for role, staff in self.schedule.items() if staff is testStaff}
        possibleSwapDays = allDays - staffWorkingDays
        staffAlreadyWorksRole = False
        for role, staff in self.schedule.items():
            if staff is testStaff and role is testRole:
                staffAlreadyWorksRole = True
                break

        return (testRole.day in possibleSwapDays or staffAlreadyWorksRole) and testStaff.isAvailable(testRole)

def numberOfDaysCouldWork(staff):
    days = 0
    for times in staff.availability.values():
        if times != []:
            days += 1
    return days

def createSchedule(roleCollection, staffCollection):
    schedule = Schedule(roles=roleCollection, staff=staffCollection)
    schedule.repairDoubles()
    logger.debug(f"Remaining doubles: {schedule.identifyDoubles()}")

    unavailables = schedule.identifyUnavailables()
    logger.debug(f"Remaining unavailabilities: {unavailables}")
    logger.debug(f"Number of unavailables: {len(unavailables)}")
    schedule.repairUnavailables()
    # schedule = repairPreferences(schedule)

    beforeUnavailables = len(unavailables)
    logger.debug(f"Remaining doubles: {Schedule.identifyDoubles(schedule)}")
    unavailables = schedule.identifyUnavailables()
    logger.debug(f"Remaining unavailabilities: {unavailables}")
    logger.debug(f"Number of unavailables: {len(unavailables)}")
    logger.debug(f"Unavailables removed: {beforeUnavailables - len(unavailables)}")

    tupleSchedule = schedule.tupleRepresentation()
    
    return tupleSchedule

def repairPreferences(schedule):
    return schedule
