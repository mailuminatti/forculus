Integrating Forculus with Github
===============================

You can integrate Forculus with Github to automatically create and delete users. To do so:

1. Create a new Personal Token in Github, preferably from a user dedicated to run automations. The token will require read organizations permissions, and read/write user permissions

2. Open the `integrations.ini` file and add

```

[github]
url = https://api.github.com/
apikey = yourlongpersonaltoken
organization = yourorganizationname

```

1. Add the Github app to your users that need access to it in the `user-access.yaml` file:


```yaml
users:
  - email: john.snow@mail.com
    username: johnsnow
    firstname: John
    lastname: Snow
    tools:
    - name: github
      role: admin
```
Valid parameters:

`role`: Can be any of `admin`, `direct_member` or `billing_manager`

---
**IMPORTANT**

When a new user is created in Github, an email is sent to the user to accept being part of the organization. If the user doesn't have a Github account, a prompt will appear to create one. Make sure that the user uses the username provided in the `username` field, otherwise it will be deleted on the next run, as the usernames in Github and `user-access.yaml` will not match.

---