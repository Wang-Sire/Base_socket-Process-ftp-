from socket import *
import os,sys
import signal
import time

# 具体功能
class FtpClient(object):
    def __init__(self,s):
        self.s = s

    def do_list(self):
        self.s.send(b"L")
        # 等待回复
        data =self.s.recv(128).decode()
        # print(data)
        if data =='OK':
            data= self.s.recv(4096).decode()
            files = data.split(',')
            print(files)
            for i in files:
                print("file:",i)
        else:        
            print(data)
    def do_get(self,filename):
        self.s.send(("G "+filename).encode())
        data = self.s.recv(128).decode()
        print(data)
        if data =="OK":
            f = open(filename,'wb')
            while True:
                data=self.s.recv(4096)
                if data == b"##":
                    break
                f.write(data)
            f.close()
        else:
            print(data)

    def do_put(self,filename):
        self.s.send(("P "+filename).encode())
        data = self.s.recv(128).decode()
        if data =='OK':
            f = open(filename,'rb')
            while True:
                data = f.read(1024)
                if not data:
                    # time.sleep(0.1)
                    self.s.send(b"@@")
                    break
                self.s.send(data)
                
                
        else:
            print(data)


    def do_quit(self):
        self.s.send(b'Q')
        self.s.close()
        sys.exit("Thanks Use!")


# 网络连接
def main():
    s = socket()
    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    try:
        s.connect(('0.0.0.0',8889))
    except Exception as e:
        print("Connect failed!",e)
        return
    # 创建文件处理类对象
    ftp = FtpClient(s)  # 将套接字属性化
    print("\n=========================")
    print("=====      list      =====")
    print("=====    get file    =====")
    print("=====    put file    =====")
    print("=====      quit  ==========")     
    while True:

        # data = s.recv(1024).decode()
        # print(data) 
        cmd =input("Please input Cmd>>>")
        # s.send(senf_s.encode())
        if  cmd.strip() == 'list':
            ftp.do_list()
        elif cmd[:3] == 'get':
            filename = cmd.strip().split(' ')[-1]
            # print(filename)
            ftp.do_get(filename)
        elif cmd[:3]== 'put':
            filename_put = cmd.strip().split(' ')[-1]
            # print(filename_put)            
            ftp.do_put(filename_put)
        elif cmd.strip() =='quit':
            ftp.do_quit()
        else:
            print("input Error,Please Repeat Input:")
            continue
    s.close()

if __name__ == "__main__":
    main()
