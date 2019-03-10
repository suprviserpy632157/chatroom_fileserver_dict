# Frame程序的配置文件
'''
框架的配置文件
'''
# 配置框架地址
frame_ip = '0.0.0.0'
frame_port = 8080
frame_address = (frame_ip,frame_port)

# 静态网页位置
STATIC_DIR = './static'

# 导入配置文件
from views import *
# 第一项为请求数据,第二项为处理函数
urls = [
    ('/time',show_time),
    ('/hello',say_hello),
    ('/bye',bye)
]