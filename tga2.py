#!/usr/bin/python -uROO

import time
import Queue as queue
import threading

def console(q):
    while True:
        q.put(raw_input('> '))
        
def business(q):
    while True:
        q.put("Business, man!")
        time.sleep(15)

if __name__ == '__main__':
    
    cmd_queue = queue.Queue()

    threading.Thread(target=console, args=(cmd_queue,)).start()
    threading.Thread(target=business, args=(cmd_queue,)).start()

    while True:
        print cmd_queue.get()
        