import json
import requests


def _request(action, **params):
    return {'action': action, 'params': params, 'version': 6}


def _invoke(action, **params):
    message = json.dumps(_request(action, **params)).encode('utf-8')
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


def create_deck(deck_name):
    return _invoke('createDeck', deck=deck_name)


def upload_media_file(filename, file_path):
    return _invoke('storeMediaFile', filename=filename, path=file_path)


def media_file_exists(filename):
    if _invoke('retrieveMediaFile', filename=filename):
        return True
    return False


def create_note_card(front, back, tags, deck, deck_type):
    notecards = [
        {"deckName": deck,
         "modelName": deck_type,
         "fields": {
             "Front": front,
             "Back": back
         },
         "tags": tags.split(",")
         }
    ]

    return _invoke("addNotes", notes=notecards)


def sync():
    _invoke("sync")
    return
