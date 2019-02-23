# ftp  文件服务器 fork server 训练
from socket import *
import  os,sys
import signal 
import time

# 可能用到的内容设置全局变量
Host = '0.0.0.0'
Port = 8889
Addr= (Host,Port)
file_lib = '/home/w/Desktop/'
# print(os.path.listdir(file_lib))

class FtpServer(object):
    def __init__(self,c):
        self.c  =c
    # 列出列表
    def do_list(self):
        # 获取文件列表
        file_list= os.listdir(file_lib)
        if not file_list:
            self.c.send("文件库为空")
            return
        else:
            self.c.send(b'OK')
            time.sleep(0.1)     # 连续的发送可能会出现粘包,所以 sleep 0.1秒
        files = ''
        for i in file_list:
            if i[0] != '.' and os.path.isfile(file_lib+i):
                files += i+','
        # 将拼接好的字符串传给客户端
        self.c.send(files.encode())

    # get file 
    def do_get(self,filename):
        try:
            fd = open(file_lib+filename,'rb')
        except IOError:
            print(filename)
            self.c.send(b"Found File!")
            return
        else:
            self.c.send(b"OK")
            time.sleep(0.1)
        # 发送文件 内容
        while True:
            data = fd.read(1024) 
            if not data:
                time.sleep(0.1)     # 防止 粘包 
                self.c.send(b"##")
                self.c.send(data)

    # put 上传文件
    def do_put(self,filename):
        sel_filename =os.listdir(file_lib)
        # print(sel_filename)
        if filename in sel_filename :
            self.c.send(b" Not  Create")
        else: 
            self.c.send(b"OK")
        try:
            f = open(file_lib+filename,'wb')
        except Exception as e:
            print(b"Not Create FileObject")
        except KeyboardInterrupt:
            sys.exit("退出成功！")
        while True:
            data = self.c.recv(4096)
            # print(data.decode())
            if data.decode() == "@@":
                break
            f.write(data)
        f.close()


        

def do_request(c):
    ftp = FtpServer(c)  # 将 c 作为类的属性 ↑ 看类__init__ 里 c
    while True:
        data =c.recv(1024).decode()
        # print(data[0])
        if  not data or data[0] == 'Q':         # 把 not data 提前防止服务端出现下标越界的情况
            c.close()
            return
        if data[0] =='L':
            ftp.do_list()
        elif data[0] == 'G':
            filename = data.split(' ')[-1]
            ftp.do_get(filename)
        elif data[0] == 'P':
            filename = data.split(' ')[-1]
            # print(filename)
            ftp.do_put(filename)
            


# 网络搭建
def main():
    s = socket()
    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    s.bind(Addr)
    s.listen(5)
    print("Listen the Port 8888")
    signal.signal(signal.SIGCHLD,signal.SIG_IGN)
#   ↑ 防止僵尸进程  ↓ 开始等待客户端
    while True:
        try:
            c,addr = s.accept()
        except KeyboardInterrupt:
            s.close()
            sys.exit("服务器退出")
        except Exception as e:
            print("Error :",e)
            continue
        print("Sucessfully Connection Client:",addr)
        #　创建子进程
        pid = os.fork()
        if pid == 0:
            s.close()  # 子进程用处理主进程的套接字，所以关闭主进程
            # data=os.listdir(file_lib)  # 列表没有　encode
            # c.send(data.encode())
            do_request(c)
            os._exit(0)
    
        else:
            c.close()# 应为主进程不处理客户端的信息，所以主进程关闭客户端链接
   
if __name__ == "__main__":
    main()
# 