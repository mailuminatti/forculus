import requests
import configparser
import json
from urllib.request import urlopen


def get_server_public_key():

    config = configparser.ConfigParser()
    config.read('integrations.ini')
    url = config['passbolt']['url']
    endpoint = url + "auth/verify.json"
    response = urlopen(endpoint)
    data_json = json.loads(response.read())
    return data_json['body']['keydata']
def integrate_users(core_users):
    passbolt_public_key = get_server_public_key()

    passbolt = passboltapi.PassboltAPI(config_path="integration_configs/passbolt_config.ini", new_keys=True)
    passbolt.get(url="/resources.json?api-version=v2")

get_server_public_key()
