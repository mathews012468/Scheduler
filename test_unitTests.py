import main, datetime, pytest

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
        schedule = main.Schedule('roles_fourShifts.txt', 'staff_single.txt')
        staff = schedule.week[0][0][1] # staff object of first day's roleStaffPair
        #This index chain shows there's a simpler way to set this up.

        assert main.shiftsRemaining(staff, schedule) == 0

    def test_2(self):
        """"staff.maxShifts=4, staff in schedule 2 times"""
        schedule = main.Schedule('roles_twoShifts.txt','staff_single.txt')
        staff = schedule.week[0][0][1]
        
        assert main.shiftsRemaining(staff, schedule) == 2

    def test_3(self):
        """staff.maxShifts=4, staff in schedule 6 times"""
        schedule = main.Schedule('roles_sixShifts.txt','staff_single.txt')
        staff = schedule.week[0][0][1]

        assert main.shiftsRemaining(staff, schedule) == -2