#encoding=utf8
import time
import config
from kazoo.client import KazooClient
from kazoo.client import KazooState

zk = KazooClient(hosts=config.server_list)
zk.start()
print zk

def my_listener(state):
    print "state:", state

zk.add_listener(my_listener)

def my_func(event):
    print "event:", event
    print "dir event:", dir(event)

children = zk.get_children("/lock", watch=my_func)

while 1:
    time.sleep(1)
