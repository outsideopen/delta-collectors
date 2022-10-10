from os import path
from threading import Semaphore

from delta import logging

FILE_NAME = "scratch.tsv"
lock = Semaphore()
logger = logging.getLogger(__name__)


def add_ip(ip):
    ips = get_ips()
    if ip not in ips:
        logger.debug(ip)
        write_file(f"{ip}\n", append=True)


def get_ips():
    contents = read_file()
    logger.debug(contents)
    result = map(lambda el: el.split("\t")[0], contents)

    return list(result)


def write_file(content, append=False):
    logger.debug('before aquire')
    lock.acquire()
    logger.debug('after aquire')

    logger.debug(content)
    logger.debug(append)

    permission = "a" if append else "w"

    with open(FILE_NAME, permission) as f:
        f.write(content)
        f.close()

    lock.release()


def read_file():

    if not path.isfile(FILE_NAME):
        return []

    lock.acquire()

    f = open(FILE_NAME, "r")
    lines = f.readlines()

    results = []
    for line in lines:
        results.append(line)

    f.close()

    lock.release()
    return results
