
import configparser
from sys import get_asyncgen_hooks
import requests
import json
from yaspin import yaspin

auth_token = ''

def authenticate():
    global auth_token

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    auth_token = config['netlify']['apikey']


def get_spaces():
    global auth_token

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['netlify']['url']
    user = config['netlify']['user']

    endpoint = url + 'accounts'
    payload = {}
    headers =  {
        'User-Agent': 'MyApp ' + user,
        'Authorization': 'Bearer ' + auth_token
        }

    response = requests.request("GET",endpoint, data=json.dumps(payload), headers=headers)
    return json.loads(response.content)

def get_users():
    global auth_token

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['netlify']['url']
    user = config['netlify']['user']
    space_slug = config['netlify']['space_slug']

    endpoint = url + space_slug + '/members'
    payload = {}
    headers =  {
        'User-Agent': 'MyApp ' + user,
        'Authorization': 'Bearer ' + auth_token
        }

    response = requests.request("GET",endpoint, data=json.dumps(payload), headers=headers)
    return json.loads(response.content)

def create_user(new_user):
    global auth_token

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['netlify']['url']
    space_slug = config['netlify']['space_slug']

    endpoint = url + space_slug + '/members'

    netlify_data = next((item for item in new_user['tools'] if item['name'] == 'netlify'), None)

    payload = {
        'email': new_user['email'],
        'role': netlify_data['role']
    }
    
    headers =  {
        'Authorization': 'Bearer ' + auth_token
        }
    response = requests.request("POST",endpoint, headers=headers, params=payload)
    return response.json()

#Return the user ID from the username
def get_user_id(username):
    global auth_token

    active_users = get_users()
    
    for user in active_users:
        if user['username'] == username:
            return user['id']
        

def remove_user(user_to_remove):
    global auth_token

    user_id = get_user_id(user_to_remove)

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['netlify']['url']

    endpoint = url + '/api/users/' + str(user_id)
    payload = {}
    headers =  {
        'Authorization': 'Bearer ' + auth_token
        }
    response = requests.request("DELETE",endpoint, data=json.dumps(payload), headers=headers)
    return response

def refresh_user(user_data):
    global auth_token

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['netlify']['url']

    user_id = get_user_id(user_data['username'])

    netlify_data = next((item for item in user_data['tools'] if item['name'] == 'netlify'), None)

    endpoint = url + 'api/v4/users/' + user_id
    payload = {
        'id': user_id,
        'email': user_data['email'],
        'username': user_data['username'],
        'first_name': user_data['firstname'],
        'last_name': user_data['lastname'],
    }
    headers = {
        'Authorization': 'Bearer ' + auth_token,
        "Content-Type":"application/json"
         }
    response = requests.request("PUT",endpoint, data=json.dumps(payload), headers=headers)
    return response

def integrate_users(core_users):
    authenticate()

    netlify_active_users  = get_users() 

    netlify_source_users = []
    for user in netlify_active_users:
        netlify_source_users.append(user['email'])

    #Obtain all the users that should be in netlify (in file)
    netlify_local_users = []
    for user in core_users['users']:
        for tool in user['tools']:
            if tool['name'] == 'netlify':
                netlify_local_users.append(user['email'])

    #Obtain list of all users that should be created in source
    netlify_users_to_create = list(set(netlify_local_users) - set(netlify_source_users))

    #Create users in source
    for new_user in netlify_users_to_create:
        user_data = next((item for item in core_users['users'] if item['email'] == new_user), None)
        result = create_user(user_data)
        if result:
            print('User ' + result['email'] + ' created in netlify')
    
    #Obtain list of all users that should not longer exist in source
    netlify_users_to_remove = list(set(netlify_source_users) - set(netlify_local_users))

    #Remove users in source
    for user_to_remove in netlify_users_to_remove:
        result = remove_user(user_to_remove)
        if result:
            print('User ' + user_to_remove + ' deleted in netlify')

    with yaspin(text="Refreshing netlify users", color="yellow") as spinner:
    
        for user_to_refresh in netlify_local_users:
            user_data = next((item for item in core_users['users'] if item['username'] == user_to_refresh), None)
            result = refresh_user(user_data)

        if result:
            spinner.ok("✅ ")
        else:
            spinner.fail("💥 ")