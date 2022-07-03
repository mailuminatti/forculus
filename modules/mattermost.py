
import configparser
import requests
import json
from yaspin import yaspin

auth_token = ''

def authenticate():
    global auth_token

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

def get_users():
    global auth_token

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
    user_list = json.loads(response.content)

    active_users = []

    for user in user_list:
        if user['delete_at'] == 0: active_users.append(user)

    return active_users

def activate_user(new_user):
    global auth_token

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['mattermost']['url']

    user_id = get_user_id(new_user)


    endpoint = url + 'api/v4/users/' + user_id + '/active'
    payload = {
                "active": True
                }
    headers =  {
        'Authorization': 'Bearer ' + auth_token
        }
    response = requests.request("PUT",endpoint, data=json.dumps(payload), headers=headers)
    return response.json()
def create_user(new_user):
    global auth_token

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['mattermost']['url']
    default_password = config['forculus']['default_password']
    
    endpoint = url + 'api/v4/users'
    payload = {
        'email': new_user['email'],
        'username': new_user['username'],
        'first_name': new_user['firstname'],
        'last_name': new_user['lastname'],
        'password': default_password
    }
    headers =  {
        'Authorization': 'Bearer ' + auth_token
        }
    response = requests.request("POST",endpoint, data=json.dumps(payload), headers=headers)

    # If the user already exists, but is deactivated:
    if json.loads(response.content)['id'] == 'app.user.save.username_exists.app_error':
        response = activate_user(new_user)



    return response

#Return the user ID from the username
def get_user_id(user):
    global auth_token
    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['mattermost']['url']
    endpoint = url + 'api/v4/users/usernames'

    payload = [user['username']]
    headers =  {
        'Authorization': 'Bearer ' + auth_token
        }

    response = requests.request("POST",endpoint, data=json.dumps(payload), headers=headers)
    user_id = json.loads(response.content)[0]['id']
    return user_id

def remove_user(user_to_remove):
    global auth_token

    user_id = get_user_id(user_to_remove)

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['mattermost']['url']

    endpoint = url + '/api/v4/users/' + str(user_id)
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
    url = config['mattermost']['url']

    user_id = get_user_id(user_data['username'])

    mattermost_data = next((item for item in user_data['tools'] if item['name'] == 'mattermost'), None)

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
    with yaspin(text="Processing Mattermost users", color="yellow") as spinner:

        authenticate()
        result=''

        # Default users needed in mattermost to work
        mattermost_default_users = [
            'appsbot',
            'boards',
            'channelexport',
            'feedbackbot',
            'playbooks',
        ]
        mattermost_active_users = get_users() 

        #Obtain all the users that are currently in mattermost
        mattermost_source_users = []
        for user in mattermost_active_users:
            mattermost_source_users.append(user['username'])

        #Obtain all the users that should be in mattermost (in file)
        mattermost_local_users = []
        for user in core_users['users']:
            for tool in user['tools']:
                if tool['name'] == 'mattermost':
                    mattermost_local_users.append(user['username'])

        #Obtain list of all users that should be created in source
        mattermost_users_to_create = list(set(mattermost_local_users) - set(mattermost_source_users) -set(mattermost_default_users))

        #Create users in source
        for new_user in mattermost_users_to_create:
            user_data = next((item for item in core_users['users'] if item['username'] == new_user), None)
            result = create_user(user_data)
            if result:
                spinner.write('> User ' + result['username'] + ' created in mattermost')
        
        #Obtain list of all users that should not longer exist in source
        mattermost_users_to_remove = list(set(mattermost_source_users) - set(mattermost_local_users) - set(mattermost_default_users))

        #Remove users in source
        
        for user_to_remove in mattermost_users_to_remove:
            result = remove_user(user_to_remove)
            if result:
                spinner.write('> User ' + user_to_remove + ' deleted in mattermost')

        
            for user_to_refresh in mattermost_local_users:
                user_data = next((item for item in core_users['users'] if item['username'] == user_to_refresh), None)
                result = refresh_user(user_data)

        if result or (result == ''):
            spinner.ok("✅ ")
        else:
            spinner.fail("💥 ")