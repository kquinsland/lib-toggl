# Setting Toggl API key

Create a `.env` file with the following content:

```shell
❯ cat scripts/.env
# Get this from https://track.toggl.com/profile
TOGGL_API_KEY=YourValueHere
```

You can use tools like [`direnv`](https://direnv.net/) to automatically set/un-set the environment variables when you [change directories](https://github.com/ohmyzsh/ohmyzsh/blob/master/plugins/direnv/direnv.plugin.zsh):

```shell
❯ cd scripts
dotenv: found '.env' file. Source it? ([Y]es/[n]o/[a]lways/n[e]ver) a
❯ env | grep TOGGL
TOGGL_API_KEY=YourValueHere
```
