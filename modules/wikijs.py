
import configparser
import requests
import json
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

def get_users():

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    token = config['wikijs']['apikey']
    endpoint = config['wikijs']['url'] + 'graphql/'

    headers = {
        'Authorization': 'Bearer ' + token 
    }

    transport = AIOHTTPTransport(url=endpoint, headers=headers)
    #transport = AIOHTTPTransport(url="https://countries.trevorblades.com/")
    client = Client(transport=transport, fetch_schema_from_transport=False)

    query = gql(
        """
        query getUsers {
        users {
            list(filter: "")
                {
                id
                name
                email
                }
            }
        }
        """
    )

    result = client.execute(query)
    return result['users']['list']

def create_user(user_data):

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    token = config['wikijs']['apikey']
    endpoint = config['wikijs']['url'] + 'graphql/'

    headers = {
        'Authorization': 'Bearer ' + token 
    }

    transport = AIOHTTPTransport(url=endpoint, headers=headers)
    client = Client(transport=transport, fetch_schema_from_transport=False)

    query = gql(
        """
        mutation createUser{
        users {
            create(
            email: """ + '"' + user_data['email'] + '"' + 
        """
            name: """ + '"' + user_data['firstname'] + ' ' + user_data['lastname'] + '"'
        """
            providerKey: "Local"
            groups: 3
            ){
            responseResult{
                succeeded
                errorCode
                slug
            }
            user{
                id
                name
                email
            }
            }

        }
        }
        """
    )

    result = client.execute(query)
    return result['users']['list']

#Return the user ID from the username
def get_user_id(username):
    active_users = get_users()
    
    for user in active_users:
        if user['username'] == username:
            return user['Id']
        

def remove_user(user_to_remove):
    jwt = authenticate()

    user_id = get_user_id(user_to_remove)

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['wikijs']['url']

    endpoint = url + '/api/users/' + str(user_id)
    payload = {}
    headers =  {
        'Authorization': 'Bearer ' + jwt
        }
    response = requests.request("DELETE",endpoint, data=json.dumps(payload), headers=headers)
    return response

def integrate_users(core_users):
    
    wikijs_active_users = get_users()

    #Obtain all the users that are currently in wikijs
    wikijs_source_users = []
    for user in wikijs_active_users:
        wikijs_source_users.append(user['email'])

    #Obtain all the users that should be in wikijs (in file)
    wikijs_local_users = []
    for user in core_users['users']:
        for tool in user['tools']:
            if tool['name'] == 'wikijs':
                wikijs_local_users.append(user['email'])

    #Obtain list of all users that should be created in source
    wikijs_users_to_create = list(set(wikijs_local_users) - set(wikijs_source_users))

    #Create users in source
    for new_user in wikijs_users_to_create:
        #Obtain all the information from the user, not just the email
        user_data = next((item for item in core_users['users'] if item['email'] == new_user), None)
        result = create_user(user_data)
        if result:
            print('User ' + result['username'] + ' created in wikijs')
    
    #Obtain list of all users that should not longer exist in source
    wikijs_users_to_remove = list(set(wikijs_source_users) - set(wikijs_local_users))

    #Remove users in source
    for user_to_remove in wikijs_users_to_remove:
        result = remove_user(user_to_remove)
        if result:
            print('User ' + user_to_remove + ' deleted in wikijs')
