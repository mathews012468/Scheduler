import reWrite, datetime

def test_isAvailable0():
    role = reWrite.Role('swing',reWrite.Weekday.MONDAY)
    staff = reWrite.Staff('Atlas',{reWrite.Weekday.MONDAY: [datetime.time(hour=8),datetime.time(hour=23)]})

    assert reWrite.isAvailable(role, staff) == True

def test_isAvailable1():
    role = reWrite.Role('swing',reWrite.Weekday.MONDAY,callTime = datetime.time(hour=13))
    staff = reWrite.Staff('Atlas',{reWrite.Weekday.MONDAY: [datetime.time(hour=14),datetime.time(hour=23)]})

    assert reWrite.isAvailable(role, staff) == False

def test_isAvailable2():
    """False in first pair, True in second pair"""
    role = reWrite.Role('swing',reWrite.Weekday.MONDAY,callTime = datetime.time(hour=13))
    staff = reWrite.Staff('Atlas',{reWrite.Weekday.MONDAY: [datetime.time(hour=8),datetime.time(hour=14),datetime.time(hour=18),datetime.time(hour=23)]})

    assert reWrite.isAvailable(role, staff) == True

def testSuite_isAvailable():
    test_isAvailable0()
    test_isAvailable1()
    test_isAvailable2()

testSuite_isAvailable()