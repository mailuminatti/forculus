import yaml
import configparser
import requests
import json


# from modules import *

from modules import gitea, portainer, github, mattermost

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
        for tool in user['tools']:
            used_integrations.append(tool['name'])
    used_integrations = list(dict.fromkeys(used_integrations))


    # All the modules have an integrate_users function
    # therefore we can just go through all the detected integrations
    # and for each of them, use the integrate_users function
    
    # To be used in the future

    # for integration in used_integrations:
    #     integration_command = integration + '.integrate_users(core_users)'
    #     exec(integration_command)

    # gitea_result = gitea.integrate_users(core_users)
    # github_result = github.integrate_users(core_users)         
    # portainer_ce_result = portainer.integrate_users(core_users)
    mattermost_result = mattermost.integrate_users(core_users)

    
    print('✅️ All tasks executed') 
    
if __name__ == "__main__":
    main()