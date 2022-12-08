import pytest
import Schedule
import datetime

openAvailability = {
                Schedule.Weekdays.MONDAY: [datetime.time(hour=8),datetime.time(hour=23)],
                Schedule.Weekdays.TUESDAY: [datetime.time(hour=8),datetime.time(hour=23)],
                Schedule.Weekdays.WEDNESDAY: [datetime.time(hour=8),datetime.time(hour=23)],
                Schedule.Weekdays.THURSDAY: [datetime.time(hour=8),datetime.time(hour=23)],
                Schedule.Weekdays.FRIDAY: [datetime.time(hour=22),datetime.time(hour=23)],
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

#print(Schedule.pairAvailableStaff(roles, staff))

class Test_Role:
    def test_0(self):
        """No calltime provided for unlisted role"""
        with pytest.raises(ValueError, match='provide callTime for test'):
            role = Schedule.Role('test',Schedule.Weekdays.TUESDAY)


class Test_isAvailable:
    def test_0(self):
        """callTime 13 in range of 8,23"""
        role = Schedule.Role('test',Schedule.Weekdays.MONDAY,callTime=datetime.time(hour=13))
        staff = Schedule.Staff('Atlas',4,{Schedule.Weekdays.MONDAY: [datetime.time(hour=8),datetime.time(hour=23)]})

        assert staff.isAvailable(role) == True

    def test_1(self):
        """callTime 13 out of range 14,23"""
        role = Schedule.Role('test',Schedule.Weekdays.MONDAY,callTime = datetime.time(hour=13))
        staff = Schedule.Staff('Atlas',4,{Schedule.Weekdays.MONDAY: [datetime.time(hour=14),datetime.time(hour=23)]})

        assert staff.isAvailable(role) == False

    def test_2(self):
        """callTime 18 out of range in first chunk (8,14), in range in second chunk (18,23)"""
        role = Schedule.Role('test',Schedule.Weekdays.MONDAY,callTime = datetime.time(hour=18))
        staff = Schedule.Staff('Atlas',4,{Schedule.Weekdays.MONDAY: [datetime.time(hour=8),datetime.time(hour=14),datetime.time(hour=18),datetime.time(hour=23)]})

        assert staff.isAvailable(role) == True