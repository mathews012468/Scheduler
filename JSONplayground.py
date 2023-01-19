from classes import Staff, Role
import json


def compileStaff_fromJSON(filePath):
    """
    input: JSON data from appscript output
    output: list of Staff objects
    """
    staffList = []
    with open(filePath) as f:
        staffCollection = json.load(f)
        for staffObject in staffCollection:
            staffList.append(Staff(**staffObject))
    return staffList

def compileRoles_fromJSON(filePath):
    rolesOfWeek = []
    with open(filePath) as f:
        roleCollection = json.load(f)
        for roleObject in roleCollection:
            rolesOfWeek.append(Role(**roleObject))
    return rolesOfWeek

roleList = compileRoles_fromJSON('input/worlddata/roleCollection.JSON')

#rolePreference as List
#qualifiedStaff as Lists


#TODO: import list of roles
#TODO: import list of staff without availability