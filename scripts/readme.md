# Setting Toggl API key

Create a `.envrc` file with the following content:

```shell
❯ cat scripts/.envrc
# Get this from https://track.toggl.com/profile
export TOGGL_API_KEY=YourValueHere
```

Then use a tool like [direnv](https://direnv.net/) to load the environment variables.
