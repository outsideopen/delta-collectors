# delta-collectors
Nextgen collectors

# Configuration

You need to have [docker installed](https://docs.docker.com/engine/install/) on your system.

Create a `.env` file that contains at least an access token, but could have other config as well:

```bash
DELTA_API_TOKEN=<Token>                           # Required
DELTA_LOG_LEVEL=[DEBUG|INFO|WARN|ERROR]           # Defaults to INFO
DELTA_API_URL=https://stage.delta.outsideopen.dev
DELTA_HYDRA_DELAY=1
DELTA_HYDRA_TASKS=1
```

# Run Manually
```bash
# Download the latest version of the container
docker pull outsideopen/delta-collectors:latest

# Run the collectors
docker run --network host -d --env-file .env -v $PWD:/app/data outsideopen/delta-collectors:latest

# --network host    -> Add the container to the host network
# -d                -> Run in background (detached)
# --env-file .env   -> Set environment variables file (see README for details)
# -v $PWD:/app/data -> Mount /app/data in the container to the current directory on the host
```

# Run automatically with Systemd

Create the file `/etc/systemd/system/delta.service` and copy the following contents (modify as needed).

```
[Unit]
Description=Delta

[Service]
Type=simple
WorkingDirectory=/home/hydrant/delta
Environment="VERSION=0.0.3"
ExecStart=docker run --network host --env-file .env  -v /home/hydrant/delta:/app/data outsideopen/delta-collectors:${VERSION}

[Install]
WantedBy=multi-user.target
```

`systemctl enable delta.service`

`systemctl start delta.service`
