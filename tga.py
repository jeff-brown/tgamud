#!/usr/bin/python -uROO

import httplib as http
import json
from sys import argv, version_info
from platform import node
from time import sleep
import gc
import os
import syslog
import ssl
import subprocess as sb
import cPickle as pickle
import urllib, re
from time import sleep
from subprocess import Popen, PIPE
import time
from Queue import Queue
from threading import Thread

DEBUG = True

def do_stuff(q):
  while True:
    print q.get(),
    q.task_done()

if __name__ == '__main__':
    '''
    if len(argv) < 2:
        print "usage %s" % (argv[0])
    '''
 
    q = Queue(maxsize=0)
    num_threads = 10
     
    for i in range(num_threads):
      worker = Thread(target=do_stuff, args=(q,))
      worker.setDaemon(DEBUG)
      worker.start()
     
    for x in range(100):
      q.put(x)
     
    q.join()