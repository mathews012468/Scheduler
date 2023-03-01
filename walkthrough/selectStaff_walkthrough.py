from classes import Staff

#this structure comes from making decisions based on the schedule restrictions.
#which, formalizing them looks like this:
'''
* A schedule where all roles are paired with a staff
* Staff shifts do not exceed their max shifts
* Staff is paired with a role they are available for
* Each role is paired with a qualified staff
* There are no doubles in the schedule
'''
    
#possibleStaff is made up of restrictions that are schedule independent:
def getPossibleStaff(role, staffCollection):
    availableStaff = [staff for staff in staffCollection if staff.isAvailable(role)]
    #log availableStaff
    qualifiedStaff = [staff for staff in staffCollection if staff.isQualified(role)]
    #log qualifiedStaff

    possibleStaff = [staff for staff in availableStaff and qualifiedStaff]
    return possibleStaff

#Now what's left is to handle the schedule dependent restrictions:
def getStaffPool(role, possibleStaff, schedule):
    noDoubles = [staff for staff in possibleStaff if not staff.isScheduled(role, schedule)]
    #log staff without doubles
    shiftsRemaining = [staff for staff in possibleStaff if staff.shiftsRemaining > 0]
    #log staff and their shifts remaining

    staffPool = [staff for staff in noDoubles and shiftsRemaining]
    return staffPool

#right now noDoubles does not take into account the Staff.doubles attribute.
# so noDoubles can be expanded to include it:
def getStaffPool(role, possibleStaff, schedule):
    noDoubles = [
    staff for staff in possibleStaff if
    staff.isScheduled(role, schedule) == False
    or
    staff.isScheduled(role, schedule) == True and staff.doubles == True
]
    shiftsRemaining = [staff for staff in possibleStaff if staff.shiftsRemaining > 0]

    staffPool = [staff for staff in noDoubles and shiftsRemaining]
    return staffPool

#Here's a function to start the last requirement:
#A schedule where all roles are paired with a staff
def SelectStaff(staffPool, schedule):
    if staffPool == []:
        staff = Staff('Unassigned',99)
    else:
        staffPool.sort(key= lambda staff: staff.shiftsRemaining(schedule), reverse= True)
        staff = staffPool[0]
    return staff

#Here's the function that puts the pieces together so far
def createSchedule(roleCollection, staffCollection):
    schedule = []
    for role in roleCollection:
        possibleStaff = getPossibleStaff(role, staffCollection)
        staffPool = getStaffPool(role, possibleStaff, schedule)
        staff = SelectStaff(staffPool, schedule)
        schedule.appened((role,staff))
    return schedule

#Now unassigned's need to be taken care of.
#So this puts me in the same spot as the schedule iterations approach.

#When unassigned staff end up in the schedule, iterate over the schedule
#find all unassigned staff
# and reassign them.
#this step can be passed by, by finding new staff at the point where Unassigned staff would be created.
#So what does that look like?

#loosening the restrictions




