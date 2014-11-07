#encoding=utf8
import logging
from os.path import basename, join
from zkclient import ZKClient, zookeeper, watchmethod
import time
import server
import config
import ujson
import threading
import redis

if 1:
    rhd = redis.Redis()

    s = rhd.get("test_key")

    data = ujson.loads(s)

    client_down_flag = 0
    for node in data["client"]["client_list"]:
        if data["client"][node].get("down", 0):
            print "client down:", node
            client_down_flag = 1
    if not client_down_flag:
        print "no client down"

    server_down_flag = 0
    for node in data["server"]["server_list"]:
        if data["server"][node].get("down", 0):
            print "server down:", node
            server_down_flag = 1
    if not server_down_flag:
        print "no server down"

if 0:
    import threading
    import time
    cond = threading.Condition()
    time.sleep(1)
    class kongbaige(threading.Thread):
        def __init__(self, cond, diaosiname):
            threading.Thread.__init__(self, name = diaosiname)
            self.cond = cond
               
        def run(self):
            self.cond.acquire() #获取锁
               
            print self.getName() + ':一支穿云箭'  #空白哥说的第一句话
            self.cond.notify()                   #唤醒其他wait状态的线程(通知西米哥 让他说话)
            #然后进入wait线程挂起状态等待notify通知(等西米哥的回复，接下来俩人就开始扯蛋)
            self.cond.wait()
               
            time.sleep(1)
            print self.getName() + ':山无棱，天地合，乃敢与君绝!'
            self.cond.notify()
            self.cond.wait()
               
            time.sleep(1)
            print self.getName() + ':紫薇！！！！(此处图片省略)'
            self.cond.notify()
            self.cond.wait()
               
            time.sleep(1)
            print self.getName() + ':是你'
            self.cond.notify()
            self.cond.wait()
               
            #这里是空白哥说的最后一段话，接下来就没有对白了
            time.sleep(1)
            print self.getName() + ':有钱吗 借点'
            self.cond.notify()             #通知西米哥
            self.cond.release()            #释放锁
               
    class ximige(threading.Thread):
        def __init__(self, cond, diaosiname):
            threading.Thread.__init__(self, name = diaosiname)
            self.cond = cond
               
        def run(self):
            self.cond.acquire()
            self.cond.wait()   #线程挂起(等西米哥的notify通知)
               
            time.sleep(1)
            print self.getName() +':千军万马来相见'
            self.cond.notify()  #说完话了notify空白哥wait的线程
            self.cond.wait()    #线程挂起等待空白哥的notify通知
               
            time.sleep(1)
            print self.getName() + ':海可枯，石可烂，激情永不散！'
            self.cond.notify()
            self.cond.wait()
               
            time.sleep(1)
            print self.getName() + ':尔康！！！(此处图片省略)'
            self.cond.notify()
            self.cond.wait()
               
            time.sleep(1)
            print self.getName() + ':是我'
            self.cond.notify()
            self.cond.wait()
               
            #这里是最后一段话，后面空白哥没接话了 所以说完就释放锁 结束线程
            time.sleep(1)
            print self.getName() + ':滚' 
            self.cond.release()
               
               
    kongbai = kongbaige(cond, '    ')
    ximi = ximige(cond, '西米')
    #尼玛下面这2个启动标志是关键，虽然是空白哥先开的口，但是不能让他先启动，
    #因为他先启动的可能直到发完notify通知了，西米哥才开始启动，
    #西米哥启动后会一直处于44行的wait状态，因为空白哥已经发完notify通知了进入wait状态了，
    #而西米哥没收到
    #造成的结果就是2根线程就一直在那挂起，什么都不干，也不扯蛋了
    ximi.start()
    kongbai.start()

if 0:
    import zk_lock
    zk = ZKClient(config.server_list)

    lock_name = zk_lock.get_lock(zk)

    print lock_name

    exit()

    while 1:
        l = zk_lock.get_lock(zk)

        print l
        raw_input(">>")

        zk_lock.release_lock(zk, l)

if 0:
    l = [1, 2, 3, 4, 5]
    item = 1
    min_i = l[0]
    close_small = None
    for i in l:
        if min_i > i:
            min_i = i
        if not close_small and i < item:
            close_small = i
        if close_small != item and close_small < i and i < item:
            close_small = i
    else:
        if not close_small:
            close_small = item
    print min_i
    print close_small

if 0:
    mutex = threading.Lock()

    def test_fun(event):
        global mutex
        print "type_name:", event.type_name
        print "state_name:", event.state_name
        zk.exists("/xyz", watchmethod(test_fun))
        mutex.release()

    zk = ZKClient(config.server_list)

    flag = 1

    zk.get("/xyz", watchmethod(test_fun))

    mutex.acquire()
    
    mutex.acquire()

    print "done."

if 0:
    #threading lock test
    mutex = threading.Lock()
    
    mutex.acquire()
    
    print "acquire done. 1"

    mutex2 = threading.Lock()

    mutex2.acquire()

    print "acquire done. 2"

if 0:
    #每个节点启动时去/work节点注册自身ip
    zk = ZKClient("127.0.0.1:4180,127.0.0.1:4181,127.0.0.1:4182")

    def save_reg_self(parent_node, node_id):
        l = zk.get(parent_node)
        ver = l[1]['version']
        data = ujson.loads(l)
        data["children"].append(node_id)
        s = ujson.dumps(data)
        try_limit = config.write_try_limit
        while try_limit:
            l = zk.get(parent_node)
            ver = l[1]['version']
            data = ujson.loads(l)
            data["children"].append(node_id)
            s = ujson.dumps(data)
            try:
                zk.set(parent_node, s, ver)
            except zookeeper.BadVersionException, reason:
                try_limit -= 1
            else:
                break
        else:
            return -1

    #print zk.get("/xyz")

    def test_fun(event):
        print "type_name:", event.type_name
        print "state_name:", event.state_name
        zk.exists("/xyz", watchmethod(test_fun))

    l = zk.create("/work", "123", config.zknode_type_ephemeral)

    raw_input(">>")

    l = zk.get("/work")
    exit()
    try:
        l = zk.get("/work/nonode")
    except zookeeper.NoNodeException, reason:
        print reason
    else:
        print l

    exit()

    print l[1]['version']
    try:
        l = zk.set("/work", "123", l[1]['version'])
    except zookeeper.BadVersionException, reason:
        print reason
    print l

    exit()

    try:
        l = zk.create("/abc", "123", 0)
    except:
        print "create fail"

    exit()

    while 1:
        time.sleep(1)
