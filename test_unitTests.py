import main, datetime, testing_code, pytest

class Test_isAvailable:
    def test_0(self):
        """callTime 13 in range of 8,23"""
        role = main.Role('swing',main.Weekday.MONDAY,callTime=datetime.time(hour=13))
        staff = main.Staff('Atlas',4,{main.Weekday.MONDAY: [datetime.time(hour=8),datetime.time(hour=23)]})

        assert main.isAvailable(role, staff) == True

    def test_1(self):
        """callTime 13 out of range 14,23"""
        role = main.Role('swing',main.Weekday.MONDAY,callTime = datetime.time(hour=13))
        staff = main.Staff('Atlas',4,{main.Weekday.MONDAY: [datetime.time(hour=14),datetime.time(hour=23)]})

        assert main.isAvailable(role, staff) == False

    def test_2(self):
        """False in first pair, True in second pair"""
        role = main.Role('swing',main.Weekday.MONDAY,callTime = datetime.time(hour=13))
        staff = main.Staff('Atlas',4,{main.Weekday.MONDAY: [datetime.time(hour=8),datetime.time(hour=14),datetime.time(hour=18),datetime.time(hour=23)]})

        assert main.isAvailable(role, staff) == True

class Test_shiftsRemaining:
    def test_1(self):
        """"staff.maxShift=4, staff in schedule 4 times"""
        weekRoleNames = testing_code.compileRoles('roles_fourShifts.txt')
        staffList = testing_code.compileStaff('staff_single.txt')
        rolesOfWeek = main.createRoles(weekRoleNames)
        
        schedule = main.createWeekSchedule(rolesOfWeek, staffList)
        staff = staffList[0]

        assert main.shiftsRemaining(staff, schedule) == 0

    def test_2(self):
        """"staff.maxShifts=4, staff in schedule 2 times"""
        weekRoleNames = testing_code.compileRoles('roles_twoShifts.txt')
        staffList = testing_code.compileStaff('staff_single.txt')
        rolesOfWeek = main.createRoles(weekRoleNames)

        schedule = main.createWeekSchedule(rolesOfWeek, staffList)
        staff = staffList[0]
        
        assert main.shiftsRemaining(staff, schedule) == 2

    def test_3(self):
        """staff.maxShifts=4, staff in schedule 6 times"""
        weekRoleNames = testing_code.compileRoles('roles_sixShifts.txt')
        staffList = testing_code.compileStaff('staff_single.txt')
        rolesOfWeek = main.createRoles(weekRoleNames)

        schedule = main.createWeekSchedule(rolesOfWeek, staffList)
        staff = staffList[0]

        assert pytest.raises(ValueError, match='ValueError: Atlas shiftsRemaing: -2')