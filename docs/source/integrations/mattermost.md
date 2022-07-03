Integrating Forculus with Mattermost
===============================

You can integrate Forculus with Mattermost to automatically create and delete users. To do so:

1. Create a new dedicated user to be used by Forculus

2. Open the `integrations.ini` file and add

```
[mattermost]
url = https://yourmattermosturl.cloud.mattermost.com/
user = useremail@mail.com
password = superstrongpassword
```
3. Ensure that a `[forculus]` section exists in the `integrations.ini` file, and the parameter `default_password` is set. For example:

```
[forculus]
default_password = 123ChangeMe!456
```
This will set the default password when new users are created

4. Add the Mattermost app to your users that need access to it:


```yaml
users:
  - email: john.snow@mail.com
    username: john.snow
    firstname: John
    lastname: Snow
    tools:
    - name: mattermost

```
Valid parameters:

