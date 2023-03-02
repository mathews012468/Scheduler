import random

def startSchedule(roleCollection, staffCollection):
    schedule = []
    for role in roleCollection:
        staff = random.choice(staffCollection)
        schedule.appened((role,staff))
    return schedule


def createSchedule(roleCollection, staffCollection):
    schedule = startSchedule(roleCollection, staffCollection)
    schedule = repairDoubles(schedule)
    schedule = repairMaxShifts(schedule)
    schedule = repairAvailability(schedule)
    schedule = repairPreferences(schedule)
    return schedule

def repairDoubles(schedule):
    return schedule

def repairMaxShifts(schedule):
    return schedule

def repairAvailability(schedule):
    return schedule

def repairPreferences(schedule):
    return schedule
