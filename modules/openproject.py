
import configparser
import requests
import json

def get_users():

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['openproject']['url']
    apikey = config['openproject']['apikey']
    endpoint = url + 'api/v3/users'

    session = requests.Session()
    session.auth = ('apikey', apikey)

    auth = session.post(endpoint)
    
    payload = {}
    headers =  {}
    response = session.request("GET",endpoint, data=json.dumps(payload), headers=headers)
    return json.loads(response.content)['_embedded']['elements']

def create_user(new_user):

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['openproject']['url']
    apikey = config['openproject']['apikey']
    endpoint = url + 'api/v3/users'

    session = requests.Session()
    session.auth = ('apikey', apikey)

    auth = session.post(endpoint)
    
    payload = {
        "lastName": new_user['LastName'],
        "firstName": new_user['FirstName'],
        "login": new_user['username'],
        "email": new_user['email'],
        "password": "123ChangeMe!456",
        "status": "active"
            }
    headers =  {"Content-Type":"application/json"}

    response = session.request("POST",endpoint, data=json.dumps(payload), headers=headers)
    return json.loads(response.content)['_embedded']['elements']

#Return the user ID from the username
def get_user_id(username):
    active_users = get_users()
    
    for user in active_users:
        if user['email'] == username:
            return user['id']
        

def remove_user(user_to_remove):

    user_id = get_user_id(user_to_remove)

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['openproject']['url']

    endpoint = url + '/api/v3/users/' + str(user_id)
    payload = {}
    headers =  {"Content-Type":"application/json"}
    response = requests.request("DELETE",endpoint, data=json.dumps(payload), headers=headers)
    return response

def integrate_users(core_users):
    
    core_users_data = core_users['users']

    openproject_active_users = get_users()

    #Obtain all the users that are currently in Openproject
    openproject_source_users = []
    for user in openproject_active_users:
        openproject_source_users.append(user['email'])

    #Obtain all the users that should be in Openproject (in file)
    openproject_local_users = []
    for user in core_users['users']:
        for tool in user['Tools']:
            if tool['Name'] == 'Openproject':
                openproject_local_users.append(user['email'])

    #Obtain list of all users that should be created in source
    openproject_users_to_create = list(set(openproject_local_users) - set(openproject_source_users))

    #Create users in source
    for new_user in openproject_users_to_create:
        user_data =  (next(x for x in core_users_data if x['email'] == new_user))
        result = create_user(user_data)
        if result:
            print('User ' + result['Username'] + ' created in Openproject')
    
    #Obtain list of all users that should not longer exist in source
    openproject_users_to_remove = list(set(openproject_source_users) - set(openproject_local_users))

    #Remove users in source
    for user_to_remove in openproject_users_to_remove:
        result = remove_user(user_to_remove)
        if result:
            print('User ' + user_to_remove + ' deleted in Openproject')
