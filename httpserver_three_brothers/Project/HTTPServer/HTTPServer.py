# !/usr/bin/env python3
# coding=utf-8

'''
第一行:声明解释器路径:可以让程序以./运行
AID httpserver v3.0
'''
# 导入常规模块
from socket import *
import sys
from threading import Thread
# 祥见笔记中的cookie
import json
# 导入配置信息
from config import *

# 向frame发送请求,创建了第二个套接字与WebFrame交互
def connect_frame(**env):
    # print(env) #结果是字典,不是长连接型服务
    s = socket()
    try:
        s.connect(frame_address)
    except Exception as e:
        print(e)
        return
    # 将请求发送给frame(字典的发送需注意格式的转换)
    s.send(json.dumps(env).encode())
    # 如果内容特别大可以循环接收,网站特别大时,需要想办法让框架容量扩大
    data = s.recv(4096*10).decode()
    # return到调用这个函数的地方
    return data

# 封装httpserver基本功能
class HTTPServer(object):
    def __init__(self,address):
        self.address = address
        # 创建套接字绑定
        self.create_socket()
        self.bind(address)
    
    # 创建套接字
    def create_socket(self):
        self.sockfd = socket()
        # 设置端口重用(调试需要,正式上线就不想要了怎么办:见config.py的debug说明)
        self.sockfd.setsockopt(SOL_SOCKET,SO_REUSEADDR,DEBUG)
    
    def bind(self,address):
        self.ip = address[0]
        self.port = address[1]
        self.sockfd.bind(address)
    
    # 启动服务
    def serve_forever(self):
        self.sockfd.listen(10)
        print("Listen the port %d..."%self.port)
        while True:
            # 异常处理
            try:
                # 多线程并发(多用IO多路复用)
                connfd,addr = self.sockfd.accept()
                print("Connect from",addr)
            except KeyboardInterrupt:
                self.sockfd.close()
                sys.exit("退出httpserver服务器")
            except Exception as e:
                print(e)
                continue
            # 启动多线程处理客户端请求
            client = Thread(target=self.handle,args=(connfd,))
            client.setDaemon(True)
            client.start()
    
    # 处理浏览器的http请求,接收请求以及解析请求
    def handle(self,connfd):
        request = connfd.recv(4096)
        # 处理客户端断开
        if not request:
            connfd.close()
            return
        request_lines = request.splitlines()
        # 获取请求行
        request_line = request_lines[0].decode('utf-8')
        print("请求:",request_line)

        # 获取请求方法和请求内容
        tmp = request_line.split(' ')
        method = tmp[0]
        path_info = tmp[1]

        # 调用一个外部函数发送请求方法和请求内容
        data = connect_frame(method= method,path_info= path_info)

        # 通过套接字向客户传入data
        self.response(connfd,data)

    # 处理返回的数据内容
    def response(self,connfd,data):
        # 根据情况组织响应
        if data != '404':
            response_handlers = "HTTP/1.1 200 OK\r\n"
        else:
            response_handlers = "HTTP/1.1 404 Not Found\r\n"
        # 响应头,响应行拼接空格,响应体
        response_handlers += '\r\n'
        response_body = data
        response = response_handlers + response_body
        connfd.send(response.encode())
        connfd.close()


httpd = HTTPServer(ADDR)
httpd.serve_forever()  #启动服务程序