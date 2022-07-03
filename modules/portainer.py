
import configparser
import requests
import json
from yaspin import yaspin
from urllib.parse import quote

auth_token = ''

def authenticate():
    global auth_token
    config = configparser.ConfigParser()
    config.read('integrations.ini')

    url = config['portainer']['url']
    user = config['portainer']['user']
    password  = config['portainer']['password']
    
    endpoint = url + 'api/auth'
    payload = {"username": user, "Password": password}
    headers =  {"Content-Type":"application/json"}
    response = requests.post(endpoint, data=json.dumps(payload), headers=headers)
    jwt = response.json()['jwt']

    return jwt

def get_users():
    jwt = authenticate()

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['portainer']['url']

    endpoint = url + 'api/users'
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
    default_password = config['forculus']['default_password']

    endpoint = url + 'api/users'
    payload = {
        "password": default_password,
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

    endpoint = url + 'api/users/' + str(user_id)
    payload = {}
    headers =  {
        'Authorization': 'Bearer ' + jwt
        }
    response = requests.request("DELETE",endpoint, data=json.dumps(payload), headers=headers)
    return response
def refresh_user(user_data):
    
    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['tool_name']['url']
    token = config['tool_name']['apikey']

    tool_name_data = next((item for item in user_data['tools'] if item['name'] == 'tool_name'), None)

    endpoint = url + 'api/v1/admin/users/' + user_data['username']
    payload = {
        'login_name' : user_data['username'],
        'source_id' : 0,
        'admin' : tool_name_data['admin'],
        'email': user_data['email'],
        'full_name' : user_data['firstname'] + ' ' + user_data['lastname']
    }
    headers = {
        'Authorization': 'Bearer ' + token,
        "Content-Type":"application/json"
         }
    response = requests.request("PATCH",endpoint, data=json.dumps(payload), headers=headers)
    return response

def integrate_users(core_users):
    
    with yaspin(text="Processing Portainer users", color="yellow") as spinner:

        portainer_active_users = get_users()

        #Obtain all the users that are currently in Portainer
        portainer_source_users = []
        for user in portainer_active_users:
            portainer_source_users.append(user['Username'])

        #Obtain all the users that should be in Portainer (in file)
        portainer_local_users = []
        for user in core_users['users']:
            for tool in user['tools']:
                if tool['name'] == 'portainer':
                    portainer_local_users.append(user['username'])

        #Obtain list of all users that should be created in source
        portainer_users_to_create = list(set(portainer_local_users) - set(portainer_source_users))

        #Create users in source
        for new_user in portainer_users_to_create:
            result = create_user(new_user)
            if result:
                spinner.write('> User ' + result['Username'] + ' created in Portainer')
        
        #Obtain list of all users that should not longer exist in source
        portainer_users_to_remove = list(set(portainer_source_users) - set(portainer_local_users))

        #Remove users in source
        for user_to_remove in portainer_users_to_remove:
            result = remove_user(user_to_remove)
            if result:
                spinner.write('> User ' + user_to_remove + ' deleted in Portainer')
    if result:
        spinner.ok("✅ ")
    else:
        spinner.fail("💥 ")
