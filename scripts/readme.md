# Setting Toggl API key

Create a `.envrc` file with the following content:

```shell
❯ cat scripts/.envrc
#!/bin/bash
# Get this from https://track.toggl.com/profile
# See: https://www.shellcheck.net/wiki/SC2155
TOGGL_API_KEY=YourValueHere
export TOGGL_API_KEY
```

Then use a tool like [direnv](https://direnv.net/) to load the environment variables.
