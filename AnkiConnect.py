import json
import requests


def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}


def invoke(action, **params):
    message = json.dumps(request(action, **params)).encode('utf-8')
    response = requests.request(action, 'http://localhost:8765', data=message)
    response = response.json()
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']
