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
    FirstName: John
    LastName: Snow
    Tools:
    - Name: github
      Role: admin
```
Valid parameters:

`Role`: Can be any of admin, direct_member or billing_manager
