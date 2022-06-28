import yaml
import configparser
import requests
import json

from modules import portainer_ce
from modules import passbolt_community
from modules import openproject
#from modules import wikijs
#from modules import droneio
from modules import gitea
from modules import mattermost


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

    if 'gitea' in used_integrations: gitea.integrate_users(core_users)
    if 'mattermost' in used_integrations: mattermost.integrate_users(core_users)
    if 'droneio' in used_integrations: droneio.integrate_users(core_users)
    if 'wikijs' in used_integrations: wikijs.integrate_users(core_users)
    if 'Openproject' in used_integrations: openproject.integrate_users(core_users)
    if 'Passbolt' in used_integrations: passbolt_community.integrate_users(core_users)
    if 'Portainer' in used_integrations: portainer_ce.integrate_users(core_users)

                
    config = config
    
if __name__ == "__main__":
    main()