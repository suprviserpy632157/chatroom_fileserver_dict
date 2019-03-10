#!usr/bin/env python3
# coding=utf-8
'''
模拟网站后端应用处理程序
httpserver v3.0
'''
from socket import *
from select import select
import json

# 导入配置文件
from settings import *
from views import *

# 创建一个应用类用于处理具体请求 
class Application(object):
    def __init__(self):
        self.ip = frame_address[0]
        self.port = frame_address[1]
        self.sockfd = socket()
        self.sockfd.bind(frame_address)
    
    # 启动后端
    def start(self):
        self.sockfd.listen(5)
        print("Listen the port %d"%self.port)
        # while True:
        #     connfd,addr = self.sockfd.accept()
        #     request = connfd.recv(1024).decode()
        #     self.handle(connfd,request)
        # 三个监听列表监听套接字 
        rlist =[self.sockfd]
        wlist = []
        xlist = []
        while True:
            # 监控客户端连接
            rs,ws,xs = select(rlist,wlist,xlist)
            for r in rs:
                # 有客户端连接
                if r is self.sockfd:
                    connfd,addr = r.accept()
                    rlist.append(connfd)
                else:
                    # 1024即可,因为前段已经整合成json格式,接收httpserver请求
                    # 此处测试可以单独打印request看能不能得到request
                    request = r.recv(1024).decode() 
                    if not request:
                        rlist.remove(r)
                        continue
                    self.handle(r,request)

    # 处理请求
    def handle(self,connfd,request):
        request = json.loads(request)
        print(request)
        # 测试代码
        # d ={'status':"200",'data':'Hello World'}
        # connfd.send(json.dumps(d).encode())
        
        # 获取request中请求方法和请求内容
        method = request['method']
        path_info = request['path_info']
        
        if method == 'GET':
            if path_info == '/' or path_info[-5:] == '.html':
                data = self.get_html(path_info)
            else:
                data = self.get_data(path_info)
        elif method == 'POST':
            pass 
        
        # 得到网页内容则发送,没得到就发送404
        if data: #如果data存在
            connfd.send(data.encode())
        else: #否则,写一个固定的小网页
            connfd.send(b'404')

    # 处理网页
    def get_html(self,path_info):
        # 判断主页
        if path_info == '/':
            get_file = STATIC_DIR + "/index.html"
        # 别的网页
        else:
            get_file = STATIC_DIR + path_info
        try:
            fd = open(get_file)
        except IOError:
            return
        else:
            return fd.read()

    # 处理数据
    def get_data(self,path_info):
        for url,func in urls:
            # 是对应urls的请求时返回对应的函数
            if path_info == url:
                return func()
        return '404'

app = Application()
app.start() #启动后端框架服务