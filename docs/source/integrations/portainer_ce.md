Integrating Forculus with Portainer
===================================

You can integrate Forculus with Portainer to automatically create and delete users. To do so:

1. Create a dedicated user in Portainer with administrative privileges 

2. Open the `integrations.ini` file and add

```
[portainer]
url = https://your.portainer.url/
user = portaineruser
password = superstrongpassword

```
3. Ensure that a `[forculus]` section exists in the `integrations.ini` file, and the parameter `default_password` is set. For example:

```
[forculus]
default_password = 123ChangeMe!456
```
This will set the default password when new users are created

4. Add the Portainer app to your users that need access to it:


```yaml
users:
  - email: john.snow@mail.com
    username: john.snow
    firstname: John
    lastname: Snow
    tools:
    - name: portainer
      role: 2
```
Valid parameters:

`role`: Sets the role for the user. `1` provides administrative privileges to the user and `2` provides non-administrative access
