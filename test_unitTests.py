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

class Test_staffDoubles:
    frontMonday = Schedule.Role('front', Schedule.Weekdays.MONDAY)
    backMonday = Schedule.Role('back', Schedule.Weekdays.MONDAY)
    lunchTuesday = Schedule.Role('lunch', Schedule.Weekdays.TUESDAY)
    auxFriday = Schedule.Role('aux', Schedule.Weekdays.FRIDAY)
    verandaFriday = Schedule.Role('veranda', Schedule.Weekdays.FRIDAY)
    staffAtlas = Schedule.Staff('Atlas',4,openAvailability)
    staffPbody = Schedule.Staff('Pbody',4,openAvailability)

    def test_0(self):
        """schedule with no doubles"""
        schedule = [(Test_staffDoubles.frontMonday, Test_staffDoubles.staffAtlas)]
        assert Schedule.staffDoubles(schedule) == []
    
    def test_1(self):
        """schedule with a single double"""
        schedule = [
            (Test_staffDoubles.frontMonday, Test_staffDoubles.staffAtlas),
            (Test_staffDoubles.backMonday, Test_staffDoubles.staffAtlas)
            ]
        assert Schedule.staffDoubles(schedule) == [1]
    
    def test_2(self):
        """schedule with no doubles across multiple days"""
        schedule = [
            (Test_staffDoubles.frontMonday, Test_staffDoubles.staffAtlas),
            (Test_staffDoubles.backMonday, Test_staffDoubles.staffPbody),
            (Test_staffDoubles.lunchTuesday, Test_staffDoubles.staffAtlas),
            (Test_staffDoubles.auxFriday, Test_staffDoubles.staffAtlas)
        ]
        assert Schedule.staffDoubles(schedule) == []
    
    def test_3(self):
        """multiple doubles across multiple days"""
        schedule = [
            (Test_staffDoubles.frontMonday, Test_staffDoubles.staffPbody),
            (Test_staffDoubles.backMonday, Test_staffDoubles.staffPbody),
            (Test_staffDoubles.lunchTuesday, Test_staffDoubles.staffAtlas),
            (Test_staffDoubles.auxFriday, Test_staffDoubles.staffAtlas),
            (Test_staffDoubles.verandaFriday, Test_staffDoubles.staffAtlas)
        ]
        assert Schedule.staffDoubles(schedule) == [1,4]


class Test_pairAvailableStaff: 
    def test_0(self):
        """pair four roles with single available staff"""
        roles = testingCode.compileRoles('roles_fourShifts.txt')
        staff = testingCode.compileStaff('staff_single.txt')
        pairings = Schedule.pairAvailableStaff(roles, staff)
        assert len(pairings) == 4
        for i in range(len(pairings)):
            assert pairings[i][0] == roles[i]
            assert pairings[i][1] == staff[0]
    
    def test_1(self):
        """pair four role with unavaiable staff"""
        roles = testingCode.compileRoles('roles_fourShifts.txt')
        staff = testingCode.compileStaff('staff_unavailable.txt')
        with pytest.raises(RuntimeError):
            Schedule.pairAvailableStaff(roles,staff)

    def test_2(self):
        """pair four roles with available staff, same maxshifts"""
        roles = testingCode.compileRoles('roles_fourShifts.txt')
        staff = testingCode.compileStaff('staff_sameMaxShifts.txt')
        #Hrm, it seems to work correctly though I'm not sure how to write a test for this.
        pass

class Test_repairDoubles:
    def test_0(self):
        """"replacing staff who has been paired on a double"""
        schedule = [
            (Schedule.Role('front',Schedule.Weekdays.MONDAY), atlas),
            (Schedule.Role('back',Schedule.Weekdays.MONDAY), atlas)
        ]
        staffList = [atlas,pbody,chell]
        assert Schedule.repairDoubles(schedule, staffList)[1][1] is not atlas


roles = testingCode.compileRoles('roles_fourShifts.txt')
staff = testingCode.compileStaff('staff_sameMaxShifts.txt')

schedule = Schedule.pairAvailableStaff(roles, staff)
Schedule.printSchedule(schedule)
