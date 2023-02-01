from classes import Role, Staff, Weekdays
import datetime
import json

staff = Staff('Tbody',3,{Weekdays.FRIDAY: []},['Support'],True)
role = Role('Support',Weekdays.TUESDAY,datetime.time(12,29),['Tbody','Dazzle','Engineer'])

schedule = [(role,staff)]

def scheduleToJSON(schedule):
    scheduleJSON = []
    for pair in schedule:
        role = pair[0]
        staff = pair[1]
        role.staff = staff.name
        scheduleJSON.append(role.toJSON())
    return scheduleJSON

jsonSchedule = scheduleToJSON(schedule)


for role in jsonSchedule:
    print(role)