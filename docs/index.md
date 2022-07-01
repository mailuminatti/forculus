# Welcome to Forculus

Forculus is an open source tool created to create/delete/update users in other tools/SaaS apps that either don't have an integration with LDAP/SSO, or if you can't afford to pay the extra value that vendors charge to have SSO integration  ([SSO TAX](https://sso.tax/))

## Use Cases

* Have a centralized manner of managing users.
* Manage tools that don't have LDAP/SSO integration.
* Lack of budget to afford the additional cost that SaaS providers put for having SSO integration.
* Manage your users through code.

## Getting Started
1. Clone this repo
2. Create an `integrations.ini` file in the root folder, detailing which tools are going to be used. For example
``` ini
[github]
url = https://api.github.com/
apikey = yourlongpersonaltoken
organization = yourorganizationname
```
3. Create an `user-access.yaml` file in the root folder, detailing which user has access to what. For example:
```yaml
users:
  - email: john.snow@mail.com
    username: johnsnow
    FirstName: John
    LastName: Snow
    Tools:
    - Name: github
      Role: admin
```
4. Install all the requirements `pip install -r requirements.txt`
5. Run it `python3 forculus-manager.py`

## Running methods
Eventhough forculus can be run locally (on your laptop), it is intended to be executed in a pipeline, while all your users remain described as code

---
**NOTE**

Take into consideration that the `integrations.ini` file will contain very sensitive information. Is recommended that you either have very restricted access to the repository that you are going to use, or that you keep the file separate

---