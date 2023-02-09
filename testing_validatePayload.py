import app
import json

def validatePayload(payload, schema):
    """ Takes in payload and checks key/value pairs against a schema """
    payloadType, schemaType = type(payload), type(schema)
    if payloadType != schemaType:
        raise ValueError(f'payload: {payload} type does not match schema: {schema}')
    
    isValid = True
    if schemaType == dict:
        if list(schema.keys()) != list(payload.keys()):
            raise KeyError(f'payload: {payload.keys()} does not match schema: {schema.keys()}')
        for key in schema.keys():
            payloadValue, schemaValue = payload[key], schema[key]
            isValueValid = validatePayload(payloadValue, schemaValue)
            isValid = isValid and isValueValid
    
    if schemaType == list:
        for payloadValue in payload:
            schemaValue = schema[0]
            isValueValid = validatePayload(payloadValue, schemaValue)
            isValid = isValid and isValueValid
    
    return isValid

file = open('input/worlddata/roleStaff_invalid.json')
schema = app.schema
payload = json.load(file)

validatePayload(payload, schema)