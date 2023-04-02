import random
import logging
from classes import Weekdays

logger = logging.getLogger(__name__)


def createSchedule(roleCollection, staffCollection):
    schedule = Schedule(roles=roleCollection, staff=staffCollection)

    unavailables = schedule.identifyUnavailables()
    logger.debug(f"Remaining unavailabilities: {unavailables}")
    logger.debug(f"Number of unavailables: {len(unavailables)}")
    schedule.repairUnavailables()

    beforeUnavailables = len(unavailables)
    unavailables = schedule.identifyUnavailables()
    logger.debug(f"Remaining unavailabilities: {unavailables}")
    logger.debug(f"Number of unavailables: {len(unavailables)}")
    logger.debug(f"Unavailables removed: {beforeUnavailables - len(unavailables)}")

    del schedule.graph
    logger.info(f"Unavailables graph deleted")

    doubles = schedule.identifyDoubles()
    DoubleCount = len(doubles)
    logger.debug(f'Before repairDoubles: {DoubleCount}')
    schedule.repairDoubles()
    remainingDoubles = schedule.identifyDoubles()
    remainingDoubleCount = len(remainingDoubles)
    logger.debug(f"Remaing doubles {remainingDoubles}")
    logger.debug(f"number of doubles: {remainingDoubleCount}")
    logger.debug(f"Doubles repaired: {DoubleCount - remainingDoubleCount}")
    
    return schedule

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
        
        MAX_ATTEMPTS = 100
        attempts = 0
        while unavailables != [] and attempts < MAX_ATTEMPTS:
            unavailableRole = random.choice(unavailables)
            self.repairUnavailable(unavailableRole)
            unavailables = self.identifyUnavailables()

            attempts += 1
            logger.debug(f"unavailable attempts: {attempts}")

        logger.debug(f"Unavailables: {unavailables}")

    def repairDoubles(self):
        doubles = self.identifyDoubles()

        MAX_ATTEMPTS = 200
        attempts = 0
        while doubles != [] and attempts < MAX_ATTEMPTS:
            doubleRole = random.choice(doubles)
            self.repairDouble(doubleRole)
            doubles = self.identifyDoubles()

            attempts += 1
            logger.debug(f"doubles attempts: {attempts}")
        logger.debug(f"Doubles: {doubles}")

    
    def repairUnavailable(self, unavailableRole):
        """
        The staff at schedule[unavailableRole] should not be available to work the current role
        they're assigned to. This function performs a series of swaps within the schedule to fix this unavailability.
        """

        """
        We need to cap the maximum cycle length we look for because this could take a LONG time with a larger number.
        Try to change this to 8 to see how long it takes! (just remember the point of this is to give us a wider range of options for fixing the schedule)
        """

        try:
            self.graph
        except AttributeError:
            self.graph = {role1: {role2: staff1.isAvailable(role2) for role2 in self.schedule} for role1, staff1 in self.schedule.items()}
            logger.info(f"Unavailbes graph created")

        logger.info(f"Unavailable role to fix: {unavailableRole}")
        MAX_LENGTH = 5
        for length in range(2,MAX_LENGTH):
            allCycles = self.allCyclesOfLength(unavailableRole, length)
            logger.debug(f"allCycles: {allCycles}")
            if allCycles == []:
                logger.warning(f"no cycles for length:{length}")
                length += 1
                continue

            cycle = random.choice(allCycles)
            logger.debug(f"Repairing: {unavailableRole}-{self.schedule[unavailableRole]}, Cycle: {[(role, self.schedule[role]) for role in cycle]}")
            self.cycleSwap(cycle)
            return
        
        logger.info(f"Currently no way of repairing {unavailableRole}")

    def repairDouble(self, doubleRole):
        logger.debug(f"Double role to repair: {doubleRole}")

        try:
            self.graph
        except AttributeError:
            self.graph = {role1: {role2: self.doublesGraph(staff1,role2) for role2 in self.schedule} for role1, staff1 in self.schedule.items()}
            logger.info(f"Doubles graph created")

        MAX_LENGTH = 5
        for length in range(2,MAX_LENGTH):
            allCycles = self.allCyclesOfLength(doubleRole, length)
            if allCycles == []:
                logger.warning(f"no cycles for length:{length}")
                length += 1
                continue
            cycle = random.choice(allCycles)
            self.cycleSwap(cycle)
            return

        logger.warning(f"{doubleRole} left unrepaired.")


    def doublesGraph(self, testStaff, testRole):
            allDays = {day for day in Weekdays}
            staffWorkingDays = {role.day for role, staff in self.schedule.items() if staff is testStaff}
            possibleSwapDays = allDays - staffWorkingDays
            staffAlreadyWorksRole = False
            for role, staff in self.schedule.items():
                if staff is testStaff and role is testRole:
                    staffAlreadyWorksRole = True
                    break

            return (testRole.day in possibleSwapDays or staffAlreadyWorksRole) and testStaff.isAvailable(testRole)

    def allCyclesOfLength(self, startRole, length):
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
        path = [startRole]
        #at the start, nothing but the node we're repairing has been visited, 
        # since the cycle we're looking for should start with that node
        visited = {role: False for role in self.graph}
        visited[startRole] = True

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
        #Question, how are these 'neighbors' It seems these are roles scattered within the graph.
        # is 'qualifyingSwapNodes' a way to think of them?
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

    def swap(self, role1, role2):
        #swap the staff in the schedule
        self.schedule[role2], self.schedule[role1] = self.schedule[role1], self.schedule[role2]

        #update the graph to reflect the swap. The rows and columns involving role1 and role2 need to be swapped.
        #This should only be done once we start fixing availabilites, so if self.graph doesn't exist, we exit.
        try:
            self.graph
        except AttributeError:
            return
        self.graph[role2], self.graph[role1] = self.graph[role1], self.graph[role2]
        for role in self.graph:
            self.graph[role][role2], self.graph[role][role1] = self.graph[role][role1], self.graph[role][role2]

    def tupleRepresentation(self):
        return [(role,staff) for role, staff in self.schedule.items()]

    def toJSON(self):
        scheduleJSON = []
        for role, staff in self.schedule.items():
            jsonObject = {}
            jsonObject['name'] = role.name
            jsonObject['staff'] = staff.name
            jsonObject['day'] = role.day.name
            jsonObject['callTime'] = role.callTime.strftime('%H:%M')
            scheduleJSON.append(jsonObject)
        return scheduleJSON

def numberOfDaysCouldWork(staff):
    days = 0
    for times in staff.availability.values():
        if times != []:
            days += 1
    if days == 0:
        #don't want someone with no availability to work
        days = -10
    return days
