import requests
import json

def postJSON(url, filePath):
    with open(filePath) as f:
        data = json.load(f)

    r = requests.post(url, json=data)

postJSON('http://127.0.0.1:5000/staffObjects',
        'input/worlddata/roleStaff.json')