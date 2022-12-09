import pytest
import Schedule
import datetime
import testingCode

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
swing = Schedule.Role('swing', Schedule.Weekdays.WEDNESDAY)
vbar = Schedule.Role('swing', Schedule.Weekdays.WEDNESDAY)

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

class Test_shiftsRemaining:
    def test_0(self):
        """staff maxShifts = 4, scheduled for 2 shifts"""
        roleStaffPairs = [(front, chell), (lunch, atlas), (middle, chell)]
        assert Schedule.shiftsRemaining(chell, roleStaffPairs) == 2
    
    def test_1(self):
        """staff maxShifts = 4, scheduled for 6 shifts"""
        roleStaffPairs = [(front, pbody), (lunch, pbody), (aux, pbody), (middle, pbody), (swing, pbody), (vbar, pbody)]
        assert Schedule.shiftsRemaining(pbody, roleStaffPairs) == -2

class Test_compileStaff:
    def test_0(self):
        """single staff"""
        staffList = testingCode.compileStaff('staff_single.txt')
        assert staffList[0].name == 'Atlas'
        assert staffList[0].maxShifts == 4
        assert staffList[0].availability == openAvailability

    def test_1(self):
        """multiple staff"""
        staffList = testingCode.compileStaff('staff_test.txt')
        assert staffList[1].name == 'Pbody'
        assert staffList[1].maxShifts == 8
        assert staffList[1].availability[Schedule.Weekdays.MONDAY] == [datetime.time(hour=4),datetime.time(hour=11),datetime.time(hour=13),datetime.time(hour=23)]

class Test_compileRoles:
    def test_0(self):
        """one day of roles"""
        roleList = testingCode.compileRoles('roles_twoShifts.txt')
        assert roleList[0].name == 'bbar'
        assert roleList[0].day == Schedule.Weekdays.MONDAY
        assert roleList[0].callTime == datetime.time(hour=16, minute=30)
    
    def test_2(self):
        """multiple days of roles"""
        roleList = testingCode.compileRoles('roles_Oct24.txt')
        thursdayroles = [role for role in roleList if role.day == Schedule.Weekdays.THURSDAY]
        assert thursdayroles[4].name =='shermans6pm'
        assert thursdayroles[4].callTime == datetime.time(hour=18, minute=00)