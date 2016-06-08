#encoding=utf8
import os
#公用配置
root_path = "/"
node_id="cli6"
server_list = "127.0.0.1:4180,127.0.0.1:4181,127.0.0.1:4182"
server_list = "192.168.86.242:7771,192.168.86.242:7772,192.168.86.242:7773"
server_list = "192.168.86.242:2181,192.168.86.242:2182,192.168.86.242:2183"
#server_list = "172.16.5.39:2181,172.16.5.39:2182,172.16.5.39:2183"

#客户端配置
#znode标志 ephemeral为临时节点，sequence为序号节点，二者可按位或
zknode_type_ephemeral = 1
zknode_type_sequence = 2
#写节点重试次数
write_try_limit=10
#处理机的父节点
client_root_path = "/work"
#server父节点
server_root_path = "/"
mail_to = ["fanyukeng@yqzbw.com"]

#lock config
lock_root_dir = "/lock_dir"
parent_node_lock_path = os.path.join(lock_root_dir, "parent_node_lock")
server_node_lock_path = os.path.join(lock_root_dir, "server_node_lock")

#服务端配置
server_node_ignore = set(["zookeeper", os.path.basename(client_root_path), os.path.basename(lock_root_dir)])
redis_host = "192.168.2.97"
redis_port = 6379
redis_db = 0
redis_key = "test_key"
server_node_ids = set(["server1", "server2", "server3"])
client_node_ids = set(["cli1", "cli2", "cli3", "cli4", "cli5", "cli6"])
