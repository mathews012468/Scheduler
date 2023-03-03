from classes import Weekdays

def staffNotWorking(schedule, doubleRole):
    notWorkingStaff = set()
    workingDay = doubleRole.day
    for role, staff in schedule:
        if role.day != workingDay:
            notWorkingStaff.add(staff)
    return list(notWorkingStaff)


def getDaysNotWorking(schedule, staff):
    daysNotWorking = []
    daysWorking = set()
    for pair in schedule:
        if pair[1] == staff:
            daysWorking.add(pair[0].day)
    for day in Weekdays:
        if day not in daysWorking:
            daysNotWorking.append(day)
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
    staffNotWorking = staffNotWorking(schedule, doubleRole)

    #for assigned staff get days not working
    daysNotWorking = getDaysNotWorking(schedule, doubleStaff)

    possibleSwaps = getPossibleSwaps(schedule, daysNotWorking, staffNotWorking)
    #sort possible swaps by staff's shifts remaining- highest at front.
    possibleSwaps.sort(key= lambda pair: pair[1][1].shiftsRemaining(schedule), reverse= True)
    swapIndex, swapRole, swapStaff= possibleSwaps[0] #(index,staff) tuple

    schedule[doubleIndex] = (doubleRole, swapStaff)
    schedule[swapIndex] = (swapRole, doubleStaff)
    
    return schedule

