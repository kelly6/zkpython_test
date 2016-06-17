#encoding=utf8

import os
from os.path import basename, join
from zkclient import ZKClient, zookeeper, watchmethod
import config
import threading

cv = threading.Condition()

flag = 1

def exist_watcher(event):
    global cv
    print "!!!!!!!!!!!!!!!!!!!!!1zk :", zk
    if event.type != zookeeper.DELETED_EVENT:
        r = zk.exists(event.path, watchmethod(exist_watcher))
    print "#####before callback acquire"
    cv.acquire()
    print "#####after callback acquire"

    cv.notify()

    cv.release()

def make_paths(zk, path, val = ''):
    path_list = path.split("/")[1:]
    cur_path = "/"
    print path_list
    for p in path_list:
        full_path = os.path.join(cur_path, p)
        try:
            zk.create(full_path, val, 0)
        except:
            pass
        cur_path = full_path

def get_lock(zk, lock_path):
    #获取不到锁时阻塞，直到获得锁
    global cv
    print "#####before begin acquire"
    cv.acquire()
    print "#####after begin acquire"

    make_paths(zk, lock_path)

    node_path = zk.create(lock_path + "/lock", "", config.zknode_type_sequence | config.zknode_type_ephemeral)
    
    children = zk.get_children(lock_path)
    node_name = os.path.basename(node_path)

    print children
    print node_name
    
    close_small = None
    min_child = children[0]
    for child in children:
        if min_child > child:
            min_child = child
        if not close_small and child < node_name:
            close_small = child
        if close_small != node_name and close_small < child and child < node_name:
            close_small = child
    else:
        if not close_small:
            close_small = node_name

    if node_name != min_child:
        r = zk.exists(lock_path + "/" + close_small, watchmethod(exist_watcher))
        if r:
            print "#####before end wait"
            cv.wait()
            print "#####after end wait"
        print "#####before end release"
        cv.release()
        print "#####after end release"
        print "node_name != min_child return"
        return node_path
    else:
        print "node_name == min_child return"
        return node_path

def try_lock(zk, lock_path):
    #获取不到锁时把自己创建的节点删除

    make_paths(zk, lock_path)

    node_path = zk.create(lock_path + "/lock", "", config.zknode_type_sequence | config.zknode_type_ephemeral)

    node_name = os.path.basename(node_path)
    
    children = zk.get_children(lock_path)
    
    min_child = children[0]
    for child in children:
        if min_child > child:
            min_child = child
    print "#### min_child:", min_child
    print "#### node_name:", node_name
    if node_name != min_child:
        zk.delete(node_path)
        return ""
    else:
        return node_path

def release_lock(zk, node_name):
    print "releasing lock"
    if not node_name:
        return 0
    zk.delete(node_name)
