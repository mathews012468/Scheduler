from classes import Weekdays, Role, Staff

class Test_isScheduled:

    def test_01(self):
        '''staff in schedule'''
        staff = Staff('Pbody',8)
        role = Role('front',Weekdays.THURSDAY)
        schedule = [(role, staff)]

        assert staff.isScheduled(role, schedule)
    
    def test_02(self):
        """staff not in schedule"""
        staff = Staff('Pbody',8)
        turret = Staff('Turret',0)
        role = Role('front',Weekdays.THURSDAY)
        schedule = [(role, turret)]

        assert staff.isScheduled(role, schedule) == False

    def test_03(self):
        """empty schedule"""
        staff = Staff('Pbody',8)
        role = Role('front',Weekdays.THURSDAY,)
        schedule = []

        assert staff.isScheduled(role, schedule) == False
        

    

