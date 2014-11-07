#encoding=utf8
import logging
from os.path import basename, join
from zkclient import ZKClient, zookeeper, watchmethod
import time

logging.basicConfig(
        level = logging.DEBUG,
        format = "[%(asctime)s] %(levelname)-8s %(message)s"
    )

log = logging

if 1:
    zk = ZKClient("127.0.0.1:4180,127.0.0.1:4181,127.0.0.1:4182")

    #print zk.get("/xyz")

    def test_fun(event):
        print "type_name:", event.type_name
        print "state_name:", event.state_name
        zk.exists("/xyz", watchmethod(test_fun))

    l = zk.exists("/xyz", watchmethod(test_fun))

    #l = zk.get_children("/", watchmethod(test_fun))

    print l

    while 1:
        time.sleep(1)
