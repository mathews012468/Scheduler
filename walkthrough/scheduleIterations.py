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

def numberOfDaysCouldWork(staff):
    days = 0
    for times in staff.availability.values():
        if times != []:
            days += 1
    return days

def createSchedule(roleCollection, staffCollection):
    schedule = Schedule(roles=roleCollection, staff=staffCollection)
    schedule.repairDoubles()

    tupleSchedule = schedule.tupleRepresentation()

    logger.debug(f"Remaining doubles: {Schedule.identifyDoubles(schedule)}")
    unavailables = identifyUnavailables(tupleSchedule)
    logger.debug(f"Remaining unavailabilities: {unavailables}")
    logger.debug(f"Number of unavailables: {len(unavailables)}")
    # schedule = repairUnavailables(schedule)
    # schedule = repairPreferences(schedule)

    # beforeUnavailables = len(unavailables)
    # logger.debug(f"Remaining doubles: {Schedule.identifyDoubles(schedule)}")
    # unavailables = identifyUnavailables(schedule)
    # logger.debug(f"Remaining unavailabilities: {unavailables}")
    # logger.debug(f"Number of unavailables: {len(unavailables)}")
    # logger.debug(f"Unavailables removed: {beforeUnavailables - len(unavailables)}")
    
    return tupleSchedule


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

def identifyUnavailables(schedule):
    """
    Return list of all role-staff pairs where the staff is
    unavailable to work the role
    """
    return [i for i, pair in enumerate(schedule) if not pair[1].isAvailable(pair[0])]

def repairPreferences(schedule):
    return schedule
