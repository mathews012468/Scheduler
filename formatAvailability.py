from classes import Weekdays
import datetime

avail ={
                "MONDAY": [],
                "TUESDAY": [],
                "WEDNESDAY": [
                    "4:30 PM",
                    "6:00 PM"
                ],
                "THURSDAY": [
                    "4:30 PM",
                    "6:00 PM"
                ],
                "FRIDAY": [
                    "4:30 PM",
                    "6:00 PM"
                ],
                "SATURDAY": [
                    "4:30 PM",
                    "6:00 PM"
                ],
                "SUNDAY": [
                    "4:30 PM",
                    "6:00 PM"
                ]
            }

availWithAM = {
                "MONDAY": [],
                "TUESDAY": [
                    "10:00 AM",
                    "1:00 PM",
                    "4:30 PM",
                    "6:00 PM",
                    "10:30 AM",
                    "12:00 PM"
                ],
                "WEDNESDAY": [],
                "THURSDAY": [
                    "4:30 PM",
                    "6:00 PM"
                ],
                "FRIDAY": [
                    "4:30 PM",
                    "6:00 PM"
                ],
                "SATURDAY": [
                    "4:30 PM",
                    "6:00 PM"
                ],
                "SUNDAY": [
                    "10:00 AM",
                    "1:00 PM",
                    "4:30 PM",
                    "6:00 PM",
                    "10:30 AM",
                    "12:00 PM"
                ]
            }

def formatAvailability(availability):
    staffAvailability = {}
    for day, callTimes in availability.items():
        weekday = Weekdays[day]
        weekdayCalltimes = [] #There's something here about creating a new empty list, when there's already a list in 'callTimes' that feels off...
        #There's a cleaner way to do this.
        for callTime in callTimes:
            hour, minutes = callTime.split(':')
            hour = int(hour)
            minutes = int(minutes[0:2])
            if hour < 12 and 'PM' in callTime:
                hour += 12
            callTime = datetime.time(hour,minutes)
            weekdayCalltimes.append(callTime)
        staffAvailability[weekday] = weekdayCalltimes
    return staffAvailability

print(formatAvailability(availWithAM))


