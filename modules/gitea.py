
import configparser
import requests
import json
from yaspin import yaspin

def get_users():

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['gitea']['url']
    token = config['gitea']['apikey']

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
    url = config['gitea']['url']
    token = config['gitea']['apikey']

    endpoint = url + 'api/v1/admin/users'
    headers = {
        'Authorization': 'Bearer ' + token,
        "Content-Type":"application/json"
         }

    payload = {
        'email': user_data['email'],
        'password': '123Changeme!456',
        'username': user_data['username'],
        'full_name': user_data['FirstName'] + ' ' + user_data['LastName']
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
    url = config['gitea']['url']
    token = config['gitea']['apikey']

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
    url = config['gitea']['url']
    token = config['gitea']['apikey']

    gitea_data = next((item for item in user_data['Tools'] if item['Name'] == 'gitea'), None)

    endpoint = url + 'api/v1/admin/users/' + user_data['username']
    payload = {
        'login_name' : user_data['username'],
        'source_id' : 0,
        'admin' : gitea_data['Admin'],
        'email': user_data['email'],
        'full_name' : user_data['FirstName'] + ' ' + user_data['LastName']
    }
    headers = {
        'Authorization': 'Bearer ' + token,
        "Content-Type":"application/json"
         }
    response = requests.request("PATCH",endpoint, data=json.dumps(payload), headers=headers)
    return response

def integrate_users(core_users):
    
    gitea_active_users = get_users()

    #Obtain all the users that are currently in gitea
    gitea_source_users = []
    for user in gitea_active_users:
        gitea_source_users.append(user['username'])

    #Obtain all the users that should be in gitea (in file)
    gitea_local_users = []
    for user in core_users['users']:
        for tool in user['Tools']:
            if tool['Name'] == 'gitea':
                gitea_local_users.append(user['username'])

    #Obtain list of all users that should be created in source
    gitea_users_to_create = list(set(gitea_local_users) - set(gitea_source_users))

    #Create users in source
    for new_user in gitea_users_to_create:
        #Obtain all the information from the user, not just the email
        user_data = next((item for item in core_users['users'] if item['username'] == new_user), None)
        result = create_user(user_data)
        if result:
            print('User ' + result['username'] + ' created in gitea')
    
    #Obtain list of all users that should not longer exist in source
    gitea_users_to_remove = list(set(gitea_source_users) - set(gitea_local_users))

    #Remove users in source
    for user_to_remove in gitea_users_to_remove:
        result = remove_user(user_to_remove)
        if result:
            print('User ' + user_to_remove + ' deleted in gitea')

    with yaspin(text="Refreshing Gitea users", color="yellow") as spinner:
    
        for user_to_refresh in gitea_local_users:
            user_data = next((item for item in core_users['users'] if item['username'] == user_to_refresh), None)
            result = refresh_user(user_data)

        if result:
            spinner.ok("✅ ")
        else:
            spinner.fail("💥 ")


    result = result
