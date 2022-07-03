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
    auth_token = config['github']['apikey']

# This function returns all the users with the tool passed as a parameter
# the list of tools reduced 
def get_list_users_tool(users, tool):

    users_with_tool = []

    for user in users:
        user_with_tool = {
            'email' : user['email'],
            'username' : user['username'],
            'firstname' : user['firstname'],
            'lastname' : user['lastname'],
            'tools' : [],
        }
        for a_tool in user['tools']:
            if a_tool['name'] == tool:
                user_with_tool['tools'] = a_tool
                users_with_tool.append(user_with_tool)
    return users_with_tool

def get_spaces():
    global auth_token

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['github']['url']
    user = config['github']['user']

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
    url = config['github']['url']
    organization = config['github']['organization']

    endpoint = url + 'orgs/'+organization+'/members'
    payload = {}
    headers =  {
        'Authorization': 'token ' + auth_token
        }

    response = requests.request("GET",endpoint, data=json.dumps(payload), headers=headers)
    return json.loads(response.content)

def create_user(new_user):
    global auth_token

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['github']['url']
    organization = config['github']['organization']

    endpoint = url + 'orgs/'+ organization + '/invitations'

    github_data = next((item for item in new_user['tools'] if item['name'] == 'github'), None)

    payload = {
        'email': new_user['email'],
        'role': github_data['role']
    }
    
    headers =  {
        'Authorization': 'Bearer ' + auth_token
        }
    response = requests.request("POST",endpoint, data=json.dumps(payload), headers=headers )
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

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['github']['url']
    organization = config['github']['organization']

    endpoint = url + 'orgs/' + organization +'/members/' + user_to_remove 

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
    url = config['github']['url']
    organization = config['github']['organization']
    #user_id = get_user_id(user_data['username'])

    github_data = next((item for item in user_data['tools'] if item['name'] == 'github'), None)

    endpoint = url + 'orgs/' + organization + '/memberships/' + user_data['username']
    payload = {
        "role": github_data['role']
        }

    headers = {
        'Authorization': 'Bearer ' + auth_token,
        "Content-Type":"application/json"
         }
    response = requests.request("PUT",endpoint, data=json.dumps(payload), headers=headers)
    return response

def integrate_users(core_users):

    with yaspin(text="Processing Github users", color="yellow") as spinner:
    
        authenticate()

        users_with_github = get_list_users_tool(core_users['users'], 'github')

        github_active_users  = get_users() 

        github_source_users = []
        for user in github_active_users:
            github_source_users.append(user['login'])

        #Obtain all the users that should be in github (in file)
        github_local_users = []
        for user in users_with_github:
            github_local_users.append(user['username'])

        #Obtain list of all users that should be created in source
        github_users_to_create = list(set(github_local_users) - set(github_source_users))

        #Create users in source
        for new_user in github_users_to_create:
            user_data = next((item for item in core_users['users'] if item['username'] == new_user), None)
            result = create_user(user_data)
            if result:
                spinner.write('> User ' + result['email'] + ' invited in github')
        
        #Obtain list of all users that should not longer exist in source
        github_users_to_remove = list(set(github_source_users) - set(github_local_users))

        #Remove users in source
        for user_to_remove in github_users_to_remove:
            result = remove_user(user_to_remove)
            if result:
                spinner.write('> User ' + user_to_remove + ' deleted in github')


        
            for user_to_refresh in github_local_users:
                user_data = next((item for item in core_users['users'] if item['username'] == user_to_refresh), None)
                result = refresh_user(user_data)

    if result:
        spinner.ok("✅ ")
    else:
        spinner.fail("💥 ")