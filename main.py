import os

if __name__ == '__main__':
    print("代理已在指定端口开启！")
    os.system("mitmdump -p 8080 -q -s intercapters.py")
