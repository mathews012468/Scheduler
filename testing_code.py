import main
import ast

def extract_data(file_line):
    return line.split("-")[1].strip()

#load input file
with open("testing/input/employee1.txt") as f:
    employees = []
    while line := f.readline():
        if line.startswith("Employee"):
            name = extract_data(line)

            #max shifts is on next line after colon
            line = f.readline()
            max_shifts = int(extract_data(line))

            weekAvailability = {}
            for i in range(7):
                weekday = main.Weekday(i)
                line = f.readline()
                dayAvailability_string = extract_data(line)
                dayAvailability = ast.literal_eval(dayAvailability_string)
                weekAvailability[weekday] = dayAvailability

            employees.append([name,max_shifts,weekAvailability])

with open("testing/input/role1.txt") as f:
    roles = []
    while line := f.readline():
        if line.startswith("Day"):
            dayname = extract_data(line).upper()
            day = main.Weekday[dayname]

            line = f.readline()
            role = extract_data(line)

            line = f.readline()
            calltime = extract_data(line)

            roles.append([day, role, calltime])

role_objs = []
for role in roles:
    day = role[0]
    role_name = role[1]
    calltime = role[2]

    new_role = main.Role(name=role_name, day=day)
    role_objs.append(new_role)

role = role_objs[0]
print(role.name)
print(role.day)
print(role.callTime)

employee_objects = []
for employee in employees:
    name = employee[0]
    max_shifts = employee[1]
    availability = employee[2]
    
    new_employee = main.Employee(name,max_shifts,availability)
    employee_objects.append(new_employee)

schedule = main.createSchedule(role_objs, employee_objects)

main.scheduleView_Restaurant(schedule)
