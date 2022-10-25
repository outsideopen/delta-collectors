# delta-collectors
Nextgen collectors

# Run

You need to have [docker installed](https://docs.docker.com/engine/install/) on your system.

Create a `.env` file that contains at least an access token, but could have other config as well:

```bash
DELTA_API_TOKEN=<My-Token>
DELTA_LOG_LEVEL=[DEBUG|INFO|WARN|ERROR]
DELTA_API_URL=https://stage.delta.outsideopen.dev
```

Run using the following command

```bash
docker run --network host --env-file .env outsideopen/delta-collectors:latest
```
