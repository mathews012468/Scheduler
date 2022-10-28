import main
#Test shiftsRemaining
#input: Employee, schedule
# Employee Object: name, max_shifts, availability
#Employee.name = string
# Employee.max_shifts = int
# Employee.availability = Dictionary Weekday(Enum): set(role names as strings)
#Schedule: a List of (Role, Employee) tuples

def chamber0():
    '''When employee object is in the schedule list, employee.max_shifts gets reduced by 1'''
    availability_1 = {main.Weekday.MONDAY: {'lunch', 'aux', 'front'}}
    subject_1 = main.Employee(name='Atlas', max_shifts=98, availability=availability_1)

    schedule = [
        (main.Role(name='aux', day=main.Weekday.MONDAY), subject_1)
        ]
        
    return print(subject_1.shiftsRemaining(schedule) == 97)

def chamber1():
    '''employee in schedule for same role on two different days times'''
    availability_1 = {main.Weekday.MONDAY: {'lunch', 'aux', 'front'}}
    subject_1 = main.Employee(name='Atlas', max_shifts=98, availability=availability_1)

    schedule = [
        (main.Role(name='aux', day=main.Weekday.MONDAY), subject_1),
        (main.Role(name='aux', day=main.Weekday.TUESDAY), subject_1)

        ]
        
    return print(subject_1.shiftsRemaining(schedule) == 96)

def chamber2():
    '''employee scheduled for same role on the same day twice'''
    availability_1 = {main.Weekday.MONDAY: {'lunch', 'aux', 'front'}}
    subject_1 = main.Employee(name='Atlas', max_shifts=98, availability=availability_1)

    schedule = [
        (main.Role(name='aux', day=main.Weekday.MONDAY), subject_1),
        (main.Role(name='aux', day=main.Weekday.MONDAY), subject_1)

        ]
        
    return print(subject_1.shiftsRemaining(schedule) == 96)


if __name__ == '__main__': #Question- Why isn't this if __name__ == '__unit_tests__'?
    chamber0()
    chamber1()
    chamber2() #Question: so how granular do I get with these testing variations?
                #TODO: Think of 'what' is being tested rather than arbirtary test repititions.