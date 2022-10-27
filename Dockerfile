FROM python:3.10.7-alpine AS builder

RUN apk add --no-cache gcc libc-dev linux-headers

WORKDIR /app

COPY . .

RUN python3 setup.py bdist_wheel


FROM alpine:3.16.2 AS production

WORKDIR /app/data

RUN apk add --no-cache gcc libc-dev linux-headers
RUN apk add --no-cache python3 python3-dev py3-pip
RUN apk add --no-cache arp-scan dhcpcd iw lldpd net-tools nmap tshark wpa_supplicant yersinia && \
    apk add --no-cache libcrypto3 libssl3 --repository=http://dl-cdn.alpinelinux.org/alpine/edge/main && \
    apk add --no-cache hydra --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community

COPY --from=builder /app/dist/delta-0.0.1-py3-none-any.whl  /tmp/
RUN pip3 install /tmp/delta-0.0.1-py3-none-any.whl


ENTRYPOINT /usr/bin/delta
