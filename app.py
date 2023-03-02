from flask import Flask
from flask import request
import main
import iterations
import logging
#logger config, timestamp and message
logging.basicConfig(filename='activity.log', filemode='w', level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object('config.DefaultConfig')
# https://flask.palletsprojects.com/en/2.2.x/config/
#app.config.from_envvar('KIKISCHEDULER_SETTINGS')

@app.route('/')
def traditions():
    return 'hello world'

@app.route('/schedule', methods=["POST"])
def createSchedule():
    roleStaffData = request.get_json()
    roleStaffSchema = app.config["SCHEMA"]
    if roleStaffData == None:
        return 'Alert: Check payload header'
    try:
        main.validatePayload(roleStaffData,roleStaffSchema)
    except ValueError as err:
        return {"error": str(err)}

    roleCollection = [main.parseRole(role) for role in roleStaffData["roles"]]
    staffCollection = [main.parseStaff(staff) for staff in roleStaffData["staff"]]

    schedule = iterations.createSchedule(roleCollection, staffCollection)

    scheduleJSON = main.scheduleToJSON(schedule)

    return scheduleJSON