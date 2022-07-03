
import configparser
import requests
import json
from yaspin import yaspin

auth_token = ''

def authenticate():
    global auth_token

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    auth_token = config['tool_name']['apikey']

def get_users():

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['tool_name']['url']
    token = config['tool_name']['apikey']

    endpoint = url + 'api/v1/admin/users'
    payload = {
        
    }
    headers =  {
        'Authorization': 'token ' + token
        }

    response = requests.request("GET",endpoint, data=json.dumps(payload), headers=headers)
    return json.loads(response.content)

def create_user(user_data):

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['tool_name']['url']
    token = config['tool_name']['apikey']
    default_password = config['forculus']['default_password']

    endpoint = url + 'api/v1/admin/users'
    headers = {
        'Authorization': 'Bearer ' + token,
        "Content-Type":"application/json"
         }

    payload = {
        'email': user_data['email'],
        'password': default_password,
        'username': user_data['username'],
        'full_name': user_data['firstname'] + ' ' + user_data['lastname']
    }
    response = requests.request("POST",endpoint, data=json.dumps(payload), headers=headers)
    return json.loads(response.content)

#Return the user ID from the username
def get_user_id(username):
    active_users = get_users()
    
    for user in active_users:
        if user['username'] == username:
            return user['Id']
        

def remove_user(user_to_remove):

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['tool_name']['url']
    token = config['tool_name']['apikey']

    endpoint = url + 'api/v1/admin/users/' + user_to_remove
    payload = {}
    headers = {
        'Authorization': 'Bearer ' + token,
        "Content-Type":"application/json"
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
    with yaspin(text="Processing tool_name users", color="yellow") as spinner:

        tool_name_active_users = get_users()

        #Obtain all the users that are currently in tool_name
        tool_name_source_users = []
        for user in tool_name_active_users:
            tool_name_source_users.append(user['username'])

        #Obtain all the users that should be in tool_name (in file)
        tool_name_local_users = []
        for user in core_users['users']:
            for tool in user['tools']:
                if tool['name'] == 'tool_name':
                    tool_name_local_users.append(user['username'])

        #Obtain list of all users that should be created in source
        tool_name_users_to_create = list(set(tool_name_local_users) - set(tool_name_source_users))

        #Create users in source
        for new_user in tool_name_users_to_create:
            #Obtain all the information from the user, not just the email
            user_data = next((item for item in core_users['users'] if item['username'] == new_user), None)
            result = create_user(user_data)
            if result:
                spinner.write('> User ' + result['username'] + ' created in tool_name')
        
        #Obtain list of all users that should not longer exist in source
        tool_name_users_to_remove = list(set(tool_name_source_users) - set(tool_name_local_users))

        #Remove users in source
        for user_to_remove in tool_name_users_to_remove:
            result = remove_user(user_to_remove)
            if result:
                spinner.write('> User ' + user_to_remove + ' deleted in tool_name')
        
        for user_to_refresh in tool_name_local_users:
            user_data = next((item for item in core_users['users'] if item['username'] == user_to_refresh), None)
            result = refresh_user(user_data)

    if result:
        spinner.ok("✅ ")
    else:
        spinner.fail("💥 ")
