import reWrite, datetime, testing_code

class isAvailable:

    def test_0():
        """callTime 13 in range of 8,23"""
        role = reWrite.Role('swing',reWrite.Weekday.MONDAY,callTime=datetime.time(hour=13))
        staff = reWrite.Staff('Atlas',4,{reWrite.Weekday.MONDAY: [datetime.time(hour=8),datetime.time(hour=23)]})

        assert reWrite.isAvailable(role, staff) == True

    def test_1():
        """callTime 13 out of range 14,23"""
        role = reWrite.Role('swing',reWrite.Weekday.MONDAY,callTime = datetime.time(hour=13))
        staff = reWrite.Staff('Atlas',4,{reWrite.Weekday.MONDAY: [datetime.time(hour=14),datetime.time(hour=23)]})

        assert reWrite.isAvailable(role, staff) == False

    def test_2():
        """False in first pair, True in second pair"""
        role = reWrite.Role('swing',reWrite.Weekday.MONDAY,callTime = datetime.time(hour=13))
        staff = reWrite.Staff('Atlas',4,{reWrite.Weekday.MONDAY: [datetime.time(hour=8),datetime.time(hour=14),datetime.time(hour=18),datetime.time(hour=23)]})

        assert reWrite.isAvailable(role, staff) == True

    def testSuite():
        isAvailable.test_0()
        isAvailable.test_1()
        isAvailable.test_2()

class shiftsRemaining:
    
    def test1():
        """"staff.maxShift=4, staff in schedule 4 times"""
        weekRoleNames = testing_code.compileRoles('roles_fourShifts.txt')
        staffList = testing_code.compileStaff('staff_single.txt')
        rolesOfWeek = reWrite.createRoles(weekRoleNames)
        
        schedule = reWrite.createWeekSchedule(rolesOfWeek, staffList)
        staff = staffList[0]

        assert reWrite.shiftsRemaining(staff, schedule) == 0

    def test2():
        """"staff.maxShifts=4, staff in schedule 2 times"""
        weekRoleNames = testing_code.compileRoles('roles_twoShifts.txt')
        staffList = testing_code.compileStaff('staff_single.txt')
        rolesOfWeek = reWrite.createRoles(weekRoleNames)

        schedule = reWrite.createWeekSchedule(rolesOfWeek, staffList)
        staff = staffList[0]
        
        assert reWrite.shiftsRemaining(staff, schedule) == 2

    def test3():
        """staff.maxShifts=4, staff in schedule 6 times"""
        weekRoleNames = testing_code.compileRoles('roles_sixShifts.txt')
        staffList = testing_code.compileStaff('staff_single.txt')
        rolesOfWeek = reWrite.createRoles(weekRoleNames)

        schedule = reWrite.createWeekSchedule(rolesOfWeek, staffList)
        staff = staffList[0]

        #this doesn't quite work. Seems pytest could handle this:
        #pytest.raises(ValueError, match='ValueError: Atlas shiftsRemaing: -2')
        assert reWrite.shiftsRemaining(staff, schedule) is ValueError

    def testSuite():
        shiftsRemaining.test1()
        shiftsRemaining.test2()
        #shiftsRemaining.test3()

#this seems to work?¿
isAvailable.testSuite()
shiftsRemaining.testSuite()

#TODO: setup and use pytest