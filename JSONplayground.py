from classes import Staff, Role
import json

with open('input/worlddata/staffCollection.JSON') as f:
    staffCollection = json.load(f)

    print(staffCollection)
    

    staff = Staff(**staffCollection[0])
