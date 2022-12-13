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

chell = Schedule.Staff('Chell', maxShifts=None, availability=None)
pbody = Schedule.Staff('Pbody', maxShifts=None, availability=None)
atlas = Schedule.Staff('Atlas', maxShifts=None, availability=None)
staff = Schedule.Staff(name='Turret',maxShifts=None, availability=None)

role = Schedule.Role(name='test', day=None, callTime=datetime.time(hour=0))


class Test_Role:
    def test_0(self):
        """No calltime provided for unlisted role"""
        with pytest.raises(ValueError, match='provide callTime for test'):
            role = Schedule.Role('test',Schedule.Weekdays.TUESDAY)


class Test_isAvailable:
    def test_0(self):
        """callTime 13 in range of 8,23"""
        role.day = Schedule.Weekdays.MONDAY
        role.callTime = datetime.time(hour=13)
        staff.availability = {Schedule.Weekdays.MONDAY: [datetime.time(hour=8),datetime.time(hour=23)]}

        assert staff.isAvailable(role) == True

    def test_1(self):
        """callTime 13 out of range 14,23"""
        role.day = Schedule.Weekdays.MONDAY
        role.callTime = datetime.time(hour=13)
        staff.availability = {Schedule.Weekdays.MONDAY: [datetime.time(hour=14),datetime.time(hour=23)]}

        assert staff.isAvailable(role) == False

    def test_2(self):
        """callTime 18 out of range in first chunk (8,14), in range in second chunk (18,23)"""
        role.day = Schedule.Weekdays.MONDAY
        role.callTime = datetime.time(hour=13)
        staff.availability = {Schedule.Weekdays.MONDAY:[
            datetime.time(hour=8),datetime.time(hour=14),
            datetime.time(hour=18),datetime.time(hour=23)]}

        assert staff.isAvailable(role) == True

class Test_shiftsRemaining:
    def test_0(self):
        """staff maxShifts = 4, scheduled for 2 shifts"""
        staff.maxShifts = 4
        roleStaffPairs = [(role, staff), (role, staff)]
        
        assert Schedule.shiftsRemaining(staff, roleStaffPairs) == 2
    
    def test_1(self):
        """staff maxShifts = 4, scheduled for 6 shifts"""
        staff.maxShifts = 4
        roleStaffPairs = [(role, staff), (role, staff), (role, staff), (role, staff), (role, staff), (role, staff)]
        
        assert Schedule.shiftsRemaining(staff, roleStaffPairs) == -2
    
    def test_2(self):
        """
        staff maxShifts = 4, scheduled for 2 shifts,
        additional staff included in roleStaffPairs
        """
        staff.maxShifts = 4
        roleStaffPairs = [(role, staff), (role, atlas), (role, staff)]

        assert Schedule.shiftsRemaining(staff, roleStaffPairs) == 2

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
    def test_0(self):
        """schedule with no doubles"""
        role.day = Schedule.Weekdays.MONDAY
        schedule = [(role, staff)]

        assert Schedule.staffDoubles(schedule) == []
    
    def test_1(self):
        """schedule with a single double"""
        role.day = Schedule.Weekdays.MONDAY
        schedule = [(role, staff), (role, staff)]

        assert Schedule.staffDoubles(schedule) == [1]
    
    def test_2(self):
        """schedule with no doubles across multiple days"""
        roleMonday = Schedule.Role('test', day=Schedule.Weekdays.MONDAY, callTime='sample')
        roleTuesday = Schedule.Role('test', day=Schedule.Weekdays.TUESDAY, callTime='sample')
        roleFriday = Schedule.Role('test', day=Schedule.Weekdays.FRIDAY, callTime='sample')

        schedule = [
            (roleMonday, staff),
            (roleMonday, atlas),
            (roleTuesday, staff),
            (roleFriday, atlas)
        ]

        assert Schedule.staffDoubles(schedule) == []
    
    def test_3(self):
        """multiple doubles across multiple days"""
        roleMonday = Schedule.Role('test', day=Schedule.Weekdays.MONDAY, callTime='sample')
        roleTuesday = Schedule.Role('test', day=Schedule.Weekdays.TUESDAY, callTime='sample')
        roleFriday = Schedule.Role('test', day=Schedule.Weekdays.FRIDAY, callTime='sample')

        schedule = [
            (roleMonday, pbody),
            (roleMonday, pbody),
            (roleTuesday, atlas),
            (roleFriday, atlas),
            (roleFriday, atlas)
        ]

        assert Schedule.staffDoubles(schedule) == [1,4]

class Test_staffWorkingToday:
    def test_0(self):
        """return list of single staff working Monday"""
        roleMonday = Schedule.Role('test', day=Schedule.Weekdays.MONDAY, callTime='sample')
        roleTuesday = Schedule.Role('test', day=Schedule.Weekdays.TUESDAY, callTime='sample')

        schedule = [
            (roleMonday, staff), (roleTuesday, staff), (roleTuesday, atlas)
        ]

        assert Schedule.staffWorkingToday(schedule,Schedule.Weekdays.MONDAY)[0] == staff

    def test_1(self):
        """return list of multiple staff working Tuesday"""
        roleMonday = Schedule.Role('test', day=Schedule.Weekdays.MONDAY, callTime='sample')
        roleTuesday = Schedule.Role('test', day=Schedule.Weekdays.TUESDAY, callTime='sample')

        schedule = [
            (roleMonday, staff), (roleTuesday, staff), (roleTuesday, atlas)
        ]
        workingList = Schedule.staffWorkingToday(schedule,Schedule.Weekdays.TUESDAY)

        assert atlas in workingList
        assert staff in workingList


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
        """pair four roles with three available staff, staff have maxshifts of 4"""
        roles = testingCode.compileRoles('roles_fourShifts.txt')
        staff = testingCode.compileStaff('staff_sameMaxShifts.txt')
        pairings = Schedule.pairAvailableStaff(roles,staff)

        for pair in pairings:
            assert Schedule.shiftsRemaining(pair[1], pairings) <= 3 and Schedule.shiftsRemaining(pair[1],pairings) >= 2
        

class Test_repairDoubles:
    def test_0(self):
        """"replacing staff who has been paired on a double"""
        role.day = Schedule.Weekdays.MONDAY
        atlas = Schedule.Staff('Atlas',4,openAvailability)
        pbody = Schedule.Staff('Pbody',4,openAvailability)
        chell = Schedule.Staff('Chell',4,openAvailability)

        schedule = [(role, atlas),(role, atlas)]
        staffList = [atlas,pbody,chell]

        assert Schedule.repairDoubles(schedule, staffList)[1][1] is not atlas

class Test_sortKey:
    def test_0(self):
        """verifying staff is sorted by shifts remaining in descending order"""
        chell.maxShifts = 4
        pbody.maxShifts = 3
        atlas.maxShifts = 2
        staffList = [chell, pbody, atlas]

        schedule = [
            (role, chell), (role, chell), (role, chell),
            (role, pbody), (role, pbody), (role, pbody)
        ]
        sortedList = Schedule.sortKey(staffList, schedule)

        assert sortedList[0] == atlas
        assert sortedList[1] == chell
        assert sortedList[2] == pbody
