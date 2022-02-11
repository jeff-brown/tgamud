#!/usr/bin/env python
"""
 File Name : tga2.py

 This script will demonstrate a simple multi-threaded game loop.

 Creation date : Thu Feb  3 20:43:03 PST 2022
 Last update : Thu Feb  3 20:43:03 PST 2022

 Created By : Jeff Bronw <jeffbr@gmail.com>
 Updated By : Jeff Brown <jeffbr@gmail.com>

 Project Goals:
    1) Demonstrate a basic multi-threaded game lookup
    2) Implement a remote access mutli-user dungeon
    3) Use ruleset based on D&D5E
"""
import logging
import socket
import time
import Queue as queue
import threading
from signal import signal, SIGPIPE, SIG_DFL
from logging.handlers import SysLogHandler

signal(SIGPIPE, SIG_DFL)
DEBUG = False

LOGFILE_FORMAT = logging.Formatter(
    '%(module)s: [%(levelname)s] %(message)s '
    '[%(pathname)s:%(funcName)s:%(lineno)d]'
)

LOGFILE_HANDLER = SysLogHandler(
    address='/var/run/syslog',
    facility='local1'
)
LOGFILE_HANDLER.setFormatter(LOGFILE_FORMAT)

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(LOGFILE_HANDLER)

if DEBUG:
    LOGGER.setLevel(logging.DEBUG)
else:
    LOGGER.setLevel(logging.INFO)


def run_server(cmd_q):
    """
    dirty little tcp server

    args:
        None

    returns:
        None
    """
    port = 23456
    backlog = 1

    # create TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    # retrieve local hostname
    local_hostname = socket.gethostname()

    # get the according IP address
    ip_address = socket.gethostbyname(local_hostname)

    # bind the socket to the port
    server_address = (ip_address, port)
    # LOGGER.warning('starting up on %s port %s', ip_address, port)
    print("starting up on {}:{}".format(ip_address,port))
    while True:
        try:
            sock.bind(server_address)
            break
        except socket.error as ex:
            LOGGER.error('Caught exception ex: %s', ex)
        time.sleep(1)

    # listen for incoming connections (server mode) with one connection
    sock.listen(backlog)
    print("wait for a connection")
    connection, _ = sock.accept()
    while True:
        print("wait for data")
        data = connection.recv(8192)
        print("data is {}".format(data))
        cmd_q.put(data)
        while not cmd_q.empty():
            print("q loop")
            try:
                item = cmd_q.get(block=False)
                print(item)
            except queue.Empty as error:
                LOGGER.error("empty queue: %s", error)
            else:
                connection.sendall(item)


def console(cmd_q):
    """
    collect user input from terminal and push it to a queue

    args:
        cmd_q (queue): the queue

    returns:
        None
    """
    while True:
        run_server(cmd_q)


def business(cmd_q):
    """
    does something in the background and then goes to sleep

    args:
        cmd_q (queue): the queue

    returns:
        None
    """
    while True:
        cmd_q.put("Business, man!")
        print("business is happening")
        time.sleep(15)


if __name__ == '__main__':
    cmd_queue = queue.Queue()

    threading.Thread(target=run_server, args=(cmd_queue,)).start()
    threading.Thread(target=business, args=(cmd_queue,)).start()
