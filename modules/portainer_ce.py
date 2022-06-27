
import configparser
import requests
import json

def authenticate():
    config = configparser.ConfigParser()
    config.read('integrations.ini')

    url = config['portainer']['url']
    user = config['portainer']['user']
    password  = config['portainer']['password']
    
    endpoint = url + '/api/auth'
    payload = {"Username": user, "Password": password}
    headers =  {"Content-Type":"application/json"}
    response = requests.post(endpoint, data=json.dumps(payload), headers=headers)
    jwt = response.json()['jwt']

    return jwt

def get_users():
    jwt = authenticate()

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['portainer']['url']

    endpoint = url + '/api/users'
    payload = {}
    headers =  {
        'Authorization': 'Bearer ' + jwt
        }
    response = requests.request("GET",endpoint, data=json.dumps(payload), headers=headers)
    return response.json()

def create_user(new_user):
    jwt = authenticate()

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['portainer']['url']

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
    url = config['portainer']['url']

    endpoint = url + '/api/users/' + str(user_id)
    payload = {}
    headers =  {
        'Authorization': 'Bearer ' + jwt
        }
    response = requests.request("DELETE",endpoint, data=json.dumps(payload), headers=headers)
    return response

def integrate_users(core_users):
    
    portainer_active_users = get_users()

    #Obtain all the users that are currently in Portainer
    portainer_source_users = []
    for user in portainer_active_users:
        portainer_source_users.append(user['Username'])

    #Obtain all the users that should be in Portainer (in file)
    portainer_local_users = []
    for user in core_users['users']:
        for tool in user['Tools']:
            if tool['Name'] == 'Portainer':
                portainer_local_users.append(user['username'])

    #Obtain list of all users that should be created in source
    portainer_users_to_create = list(set(portainer_local_users) - set(portainer_source_users))

    #Create users in source
    for new_user in portainer_users_to_create:
        result = create_user(new_user)
        if result:
            print('User ' + result['Username'] + ' created in Portainer')
    
    #Obtain list of all users that should not longer exist in source
    portainer_users_to_remove = list(set(portainer_source_users) - set(portainer_local_users))

    #Remove users in source
    for user_to_remove in portainer_users_to_remove:
        result = remove_user(user_to_remove)
        if result:
            print('User ' + user_to_remove + ' deleted in Portainer')
