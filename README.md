# delta-collectors
Nextgen collectors

# Dependencies

- [Docker Engine](https://docs.docker.com/get-docker/) `17.09.0+`
- [Docker Compose](https://docs.docker.com/compose/install/) `1.17.0+`

Docker images for `x86_64` and `arm64` architectures are provided.

The following operating systems have been tested by our team

| OS              | Version    | Architecture  |
|-----------------|------------|---------------|
| Ubuntu          | `20.04`    | `x86_64`      |
| Raspberry Pi OS | `Bullseye` | `arm64`       |
| Arch Linux      |            | `x86_64`      |


# Install

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/outsideopen/delta-collectors/HEAD/install.sh)"
```
### CAVEATS:

- Install Delta to `$HOME/delta`
- Assumes that you run docker as `root`, but install the script as a non-root user. Will prompt for a `sudo` password to start the service.
- Automatically restarts across system reboots. (See tips below on how to stop)

# Tips
Manual start: `sudo docker-compose -f $HOME/delta/docker-compose.yml up`

Manual stop:  `sudo docker-compose -f $HOME/delta/docker-compose.yml stop`

# Configuration

```bash
# $HOME/delta/.env

DELTA_API_TOKEN=<Token>                           # Required
DELTA_API_URL=https://stage.delta.outsideopen.dev

DELTA_VERSION=0.0.4                               # Defaults to latest
CANARY_VERSION=latest                             # Defaults to latest

DELTA_LOG_LEVEL=[DEBUG|INFO|WARN|ERROR]           # Defaults to INFO

DELTA_HYDRA_DELAY=1
DELTA_HYDRA_TASKS=1
```

