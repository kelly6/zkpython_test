#encoding=utf8
import logging.config
from os.path import basename, join
from zkclient import ZKClient, zookeeper, watchmethod
import time
import config
import os
import zk_lock

if 1:
    zk = ZKClient(config.server_list)

    ret = zk_lock.get_lock(zk)

    print "got lock", ret

    print "releasing lock"
    zk_lock.release_lock(zk, ret)

