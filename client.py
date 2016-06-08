#encoding=utf8

import logging.config
import os
from os.path import basename, join
from zkclient import ZKClient, zookeeper, watchmethod
import time
import config
import ujson
#import email_util
import zk_lock

def tree(zk):
    pass

if __name__ == "__main__":
    def init_logger():
        logger = logging.getLogger()
        log_path = os.getcwd() + "/log"
        log_file_name = log_path + "/zk_client.log"
        if os.path.exists(log_path):
            if not os.path.isdir(log_path):
                os.remove(log_path)
                os.makedirs(log_path)
        else:
            os.makedirs(log_path)
        fp = logging.handlers.RotatingFileHandler(log_file_name, maxBytes=10*1024*1024, mode="a", backupCount=100)
        logger.addHandler(fp)
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(filename)s] [%(lineno)d] - %(message)s")
        fp.setFormatter(formatter)
        logger.setLevel(logging.NOTSET)
        return logger

    #每个节点启动时去/work节点注册自身ip
    zk = ZKClient(config.server_list)
    print "dir zk", dir(zk)
    #try:
    #    ret = zk.delete("/worker")
    #    print "delete ret:", ret
    #except:
    #    pass
    #try:
    #    ret = zk.create("/worker", "")
    #    print "create ret:", ret
    #except Exception, reason:
    #    print "create failed", reason
    #    pass
    try:
        ret = zk.create("/worker/work", "100", zookeeper.EPHEMERAL | zookeeper.SEQUENCE)
        print "create ret:", ret
    except Exception, reason:
        print "create failed", reason
        pass
    l = zk.get_children("/")
    print "children:", l
    #work_v = zk.get("/work")
    #print "work_v:", work_v
    print "dir zookeeper", dir(zookeeper)
    exit()
    logger = init_logger()

    logger.info("logger init done.")

    def safe_reg_self(parent_node, node_id):
        l = zk.exists(parent_node)
        if not l:
            zk.create(parent_node, "{}", config.zknode_type_ephemeral)
        l = zk.exists(parent_node)
        if not l:
            print "parent_node %s not exists" % parent_node
            return -2
        #如果一直未得到锁，则在此阻塞
        lock_name = zk_lock.get_lock(zk, config.parent_node_lock_path)
        try_limit = config.write_try_limit
        #此处设置try_limit是为了防止外部程序不经过锁修改parent_node
        while try_limit:
            l = zk.get(parent_node)
            ver = l[1]['version']
            data = ujson.loads(l[0])
            data["children"] = set(data.get("children", []))
            data["children"].add(node_id)
            s = ujson.dumps(data)
            try:
                zk.set(parent_node, s, ver)
            except zookeeper.BadVersionException, reason:
                try_limit -= 1
            except Exception, reason:
                logger.error("unknown exception: " + str(reason))
                print "unkonwn excpetion:", reason
            else:
                zk.create(parent_node + "/" + node_id, "{}", config.zknode_type_ephemeral)
                #try块未出现错误
                zk_lock.release_lock(zk, lock_name)
                return 0
        else:
            #while正常结束
            zk_lock.release_lock(zk, lock_name)
            return -1

    def work_fun(zk):
        #l = zk.get("/work")
        pass

    #print zk.get("/xyz")

    def test_fun(event):
        print "type_name:", event.type_name
        print "state_name:", event.state_name
        zk.exists("/xyz", watchmethod(test_fun))

    ret = safe_reg_self(config.client_root_path, config.node_id)

    logger.info("self regist done.")

    if ret == -1:
        logger.error("reg self.fail")
        print "reg self fail"
    elif ret == -2:
        logger.error("parent node does not exist")
        print "parent node does not exist"

    try:
        while 1:
            work_fun(zk)
            time.sleep(1)
    except Exception, reason:
        logger.error("zookeeper client going wrong: " + str(reason))
        #email_util.send_mail(config.mail_to, "zookeeper client going wrong.", str(reason))
