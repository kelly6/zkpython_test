#encoding=utf8
import logging.config
from os.path import basename, join
from zkclient import ZKClient, zookeeper, watchmethod
import time
import config
import os
import redis
import zk_lock
import ujson
import email_util

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

def gen_nodes_info(zk):
    global server_set
    global client_set
    children = zk.get_children(config.server_root_path)
    ret_dic = {}
    ret_dic["server"] = {}
    ret_dic["server"]["server_list"] = list(server_set)
    cur_server = set(children) - config.server_node_ignore
    server_down_list = server_set - set(cur_server)
    for child in cur_server:
        ret_dic["server"][child] = ujson.loads(zk.get(os.path.join(config.server_root_path, child))[0])

    for child in server_down_list:
        ret_dic["server"][child] = {"down":1}

    ret_dic["client"] = {}
    ret_dic["client"]["client_list"] = list(client_set)
    cur_client = zk.get_children(config.client_root_path)

    down_list = client_set - set(cur_client)
    for child in cur_client:
        ret_dic["client"][child] = ujson.loads(zk.get(os.path.join(config.client_root_path, child))[0])
        print child, ret_dic["client"][child]
    for child in down_list:
        ret_dic["client"][child] = {"down":1}
    print ret_dic
    return ret_dic

def safe_reg_self(parent_node, node_id):
    try_limit = config.write_try_limit
    while try_limit:
        l = zk.get(parent_node)
        ver = l[1]['version']
        data = ujson.loads(l[0])
        #如果初始值不是dict,则抛弃
        if not isinstance(data, dict):
            data = {}
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
            zk.create(os.path.join(parent_node, node_id), "{}", config.zknode_type_ephemeral)
            #try块未出现错误
            return 0
    else:
        #while正常结束
        return -1

#以children节点为准，更新parent_node值
def safe_refresh_child(zk, path):
    print "####going in safe_refresh_child"
    lock_name = zk_lock.try_lock(zk, config.parent_node_lock_path)
    print "####lock_name:", lock_name
    #如果未获取到锁则不写入
    #如果服务端都未获得锁则说明客户端正在创建节点
    #可以等创建节点callback刷新
    if not lock_name:
        return 0
    children = zk.get_children(path)

    print "####" , children

    data_full = zk.get(path)
    ver = data_full[1]['version']
    data = ujson.loads(data_full[0])
    old_children = set(data.get('children', []))
    down_list = old_children - set(children)
    data['children'] = set(children)
    zk.set(path, ujson.dumps(data))

    print "####", data

    zk_lock.release_lock(zk, lock_name)
    return down_list

def children_watcher(event):
    print "in children_watcher"
    print "type_name:", event.type_name
    print "state_name:", event.state_name
    print event.type, event.connection_state, event.path
    try:
        children_nodes = zk.get_children(config.client_root_path, watchmethod(children_watcher))
    except:
        #节点被删除时会出现错误，change_watcher会在创建时重新注册watcher，这里忽略错误
        pass
    print children_nodes
    if event.type == zookeeper.CHILD_EVENT:
        #对比parent_node值与children节点名字
        down_list = safe_refresh_child(zk, config.client_root_path)
        child_down(down_list)

def change_watcher(event):
    print "in change_watcher"
    print "type_name:", event.type_name
    print "state_name:", event.state_name
    print event.type, event.connection_state, event.path
    zk.exists(config.client_root_path, watchmethod(change_watcher))

    #down_list = safe_refresh_child(zk, config.client_root_path)
    #child_down(down_list)
    #exists的watcher无法感知children动态
    #删除节点时会删除get_children watcher，创建时需要添加上
    #一般不会删除parent_node,保险起见还是添加上
    if event.type == zookeeper.CREATED_EVENT and event.path == config.client_root_path:
        zk.get_children(config.client_root_path, watchmethod(children_watcher))

#以children节点为准，更新parent_node值
def safe_refresh_server(zk, path):
    children = zk.get_children(path)

    data_full = zk.get(path)
    ver = data_full[1]['version']
    data = ujson.loads(data_full[0])
    old_children = set(data.get('children', []))
    down_list = old_children - set(children)
    print "####children:", children
    data['children'] = set(children) - config.server_node_ignore
    zk.set(path, ujson.dumps(data))

    return down_list

def server_watcher(event):
    print "in children_watcher"
    print "type_name:", event.type_name
    print "state_name:", event.state_name
    print event.type, event.connection_state, event.path
    try:
        children_nodes = zk.get_children(config.server_root_path, watchmethod(server_watcher))
    except:
        #节点被删除时会出现错误，change_watcher会在创建时重新注册watcher，这里忽略错误
        pass
    print children_nodes
    if event.type == zookeeper.CHILD_EVENT:
        #对比parent_node值与children节点名字
        down_list = safe_refresh_server(zk, config.server_root_path)
        server_down(down_list)

def server_change_watcher(event):
    print "in change_watcher"
    print "type_name:", event.type_name
    print "state_name:", event.state_name
    print event.type, event.connection_state, event.path
    zk.exists(config.server_root_path, watchmethod(server_change_watcher))

def child_down(down_list):
    if not down_list:
        return
    title = "zookeeper warning:检测到" + str(down_list) + "宕机"
    content = title
    email_util.send_mail(config.mail_to, title, content)
    logger.error(title)

def server_down(down_list):
    if not down_list:
        return
    title = "zookeeper warning:检测到zookeeper服务器" + str(down_list) + "宕机"
    content = title
    email_util.send_mail(config.mail_to, title, content)
    logger.error(title)

if __name__ == "__main__":
    logger = init_logger()
    server_set = config.server_node_ids
    client_set = config.client_node_ids
    r_dbhd = redis.Redis(host = config.redis_host, port = config.redis_port, db = config.redis_db)
    zk = ZKClient(config.server_list)

    #此处创建server端监视节点
    safe_reg_self(config.server_root_path, config.node_id)
    #try:
    #    l = zk.create(config.root_path + config.node_id, "", config.zknode_type_ephemeral)
    #    print l
    #except Exception, reason:
    #    print "create node fail:", str(reason)
    #    logger.error("create node fail:" + str(reason))
    #    exit()

    try:
        l = zk.create(config.client_root_path, "{}", 0)
        print l
    except zookeeper.NodeExistsException, reason:
        #忽略节点存在错误
        pass
    except Exception, reason:
        print "create parent node fail:", str(reason)
        logger.error("create parent node fail:" + str(reason))

    l = zk.get_children(config.client_root_path, watchmethod(children_watcher))

    l = zk.exists(config.client_root_path, watchmethod(change_watcher))

    l = zk.get_children(config.server_root_path, watchmethod(server_watcher))

    #l = zk.exists(config.server_root_path, watchmethod(server_change_watcher))

    while 1:
        nodes_info = gen_nodes_info(zk)
        nodes_info_str = ujson.dumps(nodes_info)
        r_dbhd.set(config.redis_key, nodes_info_str)
        time.sleep(1)
