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
