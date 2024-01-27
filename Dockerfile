FROM python:3.10.9-alpine AS builder

RUN apk add --no-cache gcc libc-dev linux-headers git
RUN python3 -m pip install flit
WORKDIR /app

COPY . .

RUN flit build


FROM alpine:3.19.1 AS production

WORKDIR /app/data

RUN apk add --no-cache gcc libc-dev linux-headers
RUN apk add --no-cache python3 python3-dev py3-pip
RUN apk add --no-cache arp-scan dbus-glib-dev iwd nmap && \
    apk add --no-cache libcrypto3 libssl3 --repository=http://dl-cdn.alpinelinux.org/alpine/edge/main && \
    apk add --no-cache hydra --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community

COPY --from=builder /app/dist/delta-*-py3-none-any.whl  /tmp/

RUN FILENAME=$(ls -1 /tmp/delta-*-py3-none-any.whl | tail -n1); pip3 install $FILENAME

ENTRYPOINT  ["sh", "-c", "/usr/bin/delta"]
