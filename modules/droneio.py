
import configparser
import requests
import json
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

def get_users():

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['droneio']['url']
    token = config['droneio']['apikey']

    endpoint = url + 'api/user/'
    payload = {}
    headers = {
        'Authorization': 'Bearer ' + token
         }
    response = requests.get(endpoint, data=json.dumps(payload), headers=headers)
    return json.loads(response.content)

def create_user(user_data):

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['droneio']['url']
    token = config['droneio']['apikey']

    endpoint = url + 'api/user/'
    payload = {
        "login": user_data['username'],
        "email": user_data['email'],
        "active": True
        }
    headers = {
        'Authorization': 'Bearer ' + token
         }
    response = requests.post(endpoint, data=json.dumps(payload), headers=headers)
    return json.loads(response.content)

#Return the user ID from the username
def get_user_id(username):
    active_users = get_users()
    
    for user in active_users:
        if user['Username'] == username:
            return user['Id']
        

def remove_user(user_to_remove):

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['droneio']['url']
    token = config['droneio']['apikey']

    endpoint = url + 'api/user/' + user_to_remove
    payload = {}
    headers = {
        'Authorization': 'Bearer ' + token
         }
    response = requests.delete(endpoint, data=json.dumps(payload), headers=headers)
    return json.loads(response.content)

def integrate_users(core_users):
    
    droneio_active_users = get_users()

    #Obtain all the users that are currently in droneio
    droneio_source_users = []
    # for user in droneio_active_users:
    #     droneio_source_users.append(user['email'])

    #Obtain all the users that should be in droneio (in file)
    droneio_local_users = []
    for user in core_users['users']:
        for tool in user['Tools']:
            if tool['Name'] == 'droneio':
                droneio_local_users.append(user['email'])

    #Obtain list of all users that should be created in source
    droneio_users_to_create = list(set(droneio_local_users) - set(droneio_source_users))

    #Create users in source
    for new_user in droneio_users_to_create:
        #Obtain all the information from the user, not just the email
        user_data = next((item for item in core_users['users'] if item['email'] == new_user), None)
        result = create_user(user_data)
        if result:
            print('User ' + result['Username'] + ' created in droneio')
    
    #Obtain list of all users that should not longer exist in source
    droneio_users_to_remove = list(set(droneio_source_users) - set(droneio_local_users))

    #Remove users in source
    for user_to_remove in droneio_users_to_remove:
        result = remove_user(user_to_remove)
        if result:
            print('User ' + user_to_remove + ' deleted in droneio')
