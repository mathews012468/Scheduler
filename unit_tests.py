import reWrite, datetime

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

isAvailable.testSuite()