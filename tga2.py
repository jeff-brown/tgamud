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

import time
import Queue as queue
import threading


def console(cmd_q):
    """
    collect user input from terminal and push it to a queue

    args:
        cmd_q (queue): the queue

    returns:
        None
    """
    while True:
        cmd_q.put(input('> '))


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
        time.sleep(15)


if __name__ == '__main__':
    cmd_queue = queue.Queue()

    threading.Thread(target=console, args=(cmd_queue,)).start()
    threading.Thread(target=business, args=(cmd_queue,)).start()

    while True:
        print(cmd_queue.get())
