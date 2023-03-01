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

def repairDoubles():
    pass

def repairMaxShifts():
    pass

def repairAvailability():
    pass

def repairPreferences():
    pass
