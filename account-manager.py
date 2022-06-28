import yaml
import configparser
import requests
import json

from modules import *

def main():
    print("Loading list of users")

    # Load all the users

    with open("user-access.yaml", "r") as stream:
        try:
            core_users = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    # Determine all the used integrations

    used_integrations = []
    for user in core_users['users']:
        for tool in user['Tools']:
            used_integrations.append(tool['Name'])
    used_integrations = list(dict.fromkeys(used_integrations))


    # All the modules have an integrate_users function
    # therefore we can just go through all the detected integrations
    # and for each of them, use the integrate_users function
    for integration in used_integrations:
        integration_command = integration + '.integrate_users(core_users)'
        exec(integration_command)

                
    config = config
    
if __name__ == "__main__":
    main()