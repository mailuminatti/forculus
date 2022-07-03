Integrating Forculus with Gitea
===============================

You can integrate Forculus with Gitea to automatically create and delete users. To do so:

1. Create a new Token by going to (Click on your avatar)/Settings/Applications and generate a New Token.

1. Open the `integrations.ini` file and add

```
[gitea]
url = https://your.gitea.url/
apikey = newlygeneratedtoken10wd9d9f90293eieef3
```
3. Ensure that a `[forculus]` section exists in the `integrations.ini` file, and the parameter `default_password` is set. For example:

```
[forculus]
default_password = 123ChangeMe!456
```
This will set the default password when new users are created

4. Add the Gitea app to your users that need access to it:


```yaml
users:
  - email: john.snow@mail.com
    username: john.snow
    firstname: John
    lastname: Snow
    tools:
    - name: gitea
      admin: true
```
Valid parameters:

`admin`: Grants administrative privileges to the Gitea user 
