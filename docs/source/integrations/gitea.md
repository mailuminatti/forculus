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

1. Add the Gitea app to your users that need access to it:


```