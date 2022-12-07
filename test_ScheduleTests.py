import Schedule
import datetime

openAvailability = {
                Schedule.Weekdays.MONDAY: [datetime.time(hour=8),datetime.time(hour=23)],
                Schedule.Weekdays.TUESDAY: [datetime.time(hour=8),datetime.time(hour=23)],
                Schedule.Weekdays.WEDNESDAY: [datetime.time(hour=8),datetime.time(hour=23)],
                Schedule.Weekdays.THURSDAY: [datetime.time(hour=8),datetime.time(hour=23)],
                Schedule.Weekdays.FRIDAY: [datetime.time(hour=8),datetime.time(hour=23)],
                Schedule.Weekdays.SATURDAY: [datetime.time(hour=8),datetime.time(hour=23)],
                Schedule.Weekdays.SUNDAY: [datetime.time(hour=8),datetime.time(hour=23)]
                }

chell = Schedule.Staff('Chell', 4, openAvailability)
pbody = Schedule.Staff('Pbody', 4, openAvailability)
atlas = Schedule.Staff('Atlas', 4, openAvailability)

staff = [chell, pbody, atlas]

front = Schedule.Role('front', Schedule.Weekdays.MONDAY)
lunch = Schedule.Role('lunch', Schedule.Weekdays.MONDAY)
aux = Schedule.Role('aux', Schedule.Weekdays.MONDAY)
middle = Schedule.Role('middle', Schedule.Weekdays.FRIDAY)

roles = [front, lunch, aux, middle]

print(Schedule.pairAvailableStaff(roles, staff))
