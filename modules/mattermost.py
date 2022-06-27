
import configparser
import requests
import json

def authenticate():
    config = configparser.ConfigParser()
    config.read('integrations.ini')

    url = config['mattermost']['url']
    user = config['mattermost']['user']
    password  = config['mattermost']['password']
    
    endpoint = url + 'api/v4/users/login'
    payload = {"login_id": user, "password": password}
    headers =  {"Content-Type":"application/json"}

    response = requests.post(endpoint, data=json.dumps(payload), headers=headers)

    response_headers = response.headers
    response_data = response.headers.__dict__['_store']
    auth_token = response_data['token'][1]

    return auth_token

def get_users():
    auth_token = authenticate()

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['mattermost']['url']

    endpoint = url + 'api/v4/users'
    payload = {
        "active": True
    }
    headers =  {
        'Authorization': 'Bearer ' + auth_token
        }

    response = requests.request("GET",endpoint, data=json.dumps(payload), headers=headers)
    return json.loads(response.content)

def create_user(new_user):
    jwt = authenticate()

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['mattermost']['url']

    endpoint = url + '/api/users'
    payload = {
        "password": "12ChangeMe!34",
        "role": 2,
        "username": new_user
    }
    headers =  {
        'Authorization': 'Bearer ' + jwt
        }
    response = requests.request("POST",endpoint, data=json.dumps(payload), headers=headers)
    return response.json()

#Return the user ID from the username
def get_user_id(username):
    active_users = get_users()
    
    for user in active_users:
        if user['Username'] == username:
            return user['Id']
        

def remove_user(user_to_remove):
    jwt = authenticate()

    user_id = get_user_id(user_to_remove)

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['mattermost']['url']

    endpoint = url + '/api/users/' + str(user_id)
    payload = {}
    headers =  {
        'Authorization': 'Bearer ' + jwt
        }
    response = requests.request("DELETE",endpoint, data=json.dumps(payload), headers=headers)
    return response

def integrate_users(core_users):
    
    mattermost_active_users = get_users()

    #Obtain all the users that are currently in mattermost
    mattermost_source_users = []
    for user in mattermost_active_users:
        mattermost_source_users.append(user['Username'])

    #Obtain all the users that should be in mattermost (in file)
    mattermost_local_users = []
    for user in core_users['users']:
        for tool in user['Tools']:
            if tool['Name'] == 'mattermost':
                mattermost_local_users.append(user['username'])

    #Obtain list of all users that should be created in source
    mattermost_users_to_create = list(set(mattermost_local_users) - set(mattermost_source_users))

    #Create users in source
    for new_user in mattermost_users_to_create:
        result = create_user(new_user)
        if result:
            print('User ' + result['Username'] + ' created in mattermost')
    
    #Obtain list of all users that should not longer exist in source
    mattermost_users_to_remove = list(set(mattermost_source_users) - set(mattermost_local_users))

    #Remove users in source
    for user_to_remove in mattermost_users_to_remove:
        result = remove_user(user_to_remove)
        if result:
            print('User ' + user_to_remove + ' deleted in mattermost')
