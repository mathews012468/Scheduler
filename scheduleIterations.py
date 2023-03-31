import random
import logging
from classes import Weekdays

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


    def identifyUnavailables(self):
        """
        Return list of all roles where the staff is unavailable to work the role
        """
        return [role for role, staff in self.schedule.items() if not staff.isAvailable(role)]
    

    def repairUnavailables(self):
        unavailables = self.identifyUnavailables()
        
        MAX_ATTEMPTS = 100
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
        they're assigned to. This function performs a series of swaps within the schedule to fix this unavailability.
        """

        """
        We need to cap the maximum cycle length we look for because this could take a LONG time with a larger number.
        Try to change this to 8 to see how long it takes! (just remember the point of this is to give us a wider range of options for fixing the schedule)
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
            self.cycleSwap(cycle)
            return
        
        logger.info(f"Currently no way of repairing {unavailableRole}")

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

    def allCyclesOfLength(self, unavailableRole, length):
        """
        Find all groups of roles in the schedule of size 'length' involving the 'unavailableRole'
        where the staff can be shuffled around while respecting doubles and availability.

        For example, if we're trying to find a group of size 3, we want to find three roles where
        staff1 could work role2, staff2 could work role3, and staff3 could work role1.

        This is like a wrapper around the 'allCyclesOfLengthHelper' function to avoid setting up the path, and visited lists
        in the 'repairUnavailable' function.

        Return list[list of roles in the schedule forming the cycle]
        """

        """
        graph is an adjacency matrix, it describes which role-staff pairs are connected to other role-staff pairs
        graph is an dict of dicts, it's structured so that self.graph[role1][role2] tells you if the staff
        working role1 could work role2. If that's true, then staff1 could be reassigned to role2 without breaking
        doubles/availability.
        """
        #only do this once
        #rebuilding the graph every time we fix a role-staff pair was making this program run VERY slow
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
        Find all paths of length 'length' in 'self.graph' building off of path 
        and ending at the start of path (which makes a cycle). 
        Graph is an adjacency matrix. self.graph[role1][role2] tells you if the staff working role1 could work role2
        Path is a list of the elements in the path so far (list[role])
        Length is an int representing how many more nodes we need to walk along in the path
        visited is a dictionary letting us know which nodes have been visited (so we don't visit them again)

        Return a list[list[role]]
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
            #we need a copy of visited because we don't want changes to visited in one function
            #call to mess with visited in another function call
            newVisited = {role: didVisit for role, didVisit in visited.items()}
            newVisited[neighbor] = True
            logger.debug(f"currentNode: {currentNode}, neighbor: {neighbor}")
            newCycles = self.allCyclesOfLengthHelper(length-1, path + [neighbor], newVisited)
            logger.debug(f"neighbor: {neighbor}, newCycles: {newCycles}")
            cycles.extend(newCycles)
        return cycles

def cycleSwap(self, cycle):
        """
        Perform the sequence of swaps indicated by the cycle
        If cycle is [role1, role2, role3], staff working role1 gets reassigned to role2, staff working role2 gets reassigned to role3, staff working role3 gets reassigned to role1
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
