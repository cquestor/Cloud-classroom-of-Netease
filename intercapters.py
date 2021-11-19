import re
import json
import threading
import mitmproxy
from Crypto.Cipher import AES


URL = ""  # m3u8文件地址/视频地址
VIDEONAME = ""  # 视频名称
FILE = ""  # m3u8文件
MSGSPATH = "./msgs/"  # 信息存储文件，注意末尾的'/'不能少
KEYSPATH = "./keys/"  # key存储文件，注意末尾的'/'不能少


def keyDownloader(url, text, key, name):
    """存放加密视频信息
    """
    global MSGSPATH, KEYSPATH
    msg = {
        'url': url,
        'text': text
    }
    msgFile = MSGSPATH + name.rsplit('.', 1)[0] + '.txt'
    keyFile = KEYSPATH + name.rsplit('.', 1)[0] + '.txt'
    with open(msgFile, 'w', encoding='utf-8') as f:
        json.dump(msg, f)
    with open(keyFile, 'wb') as f:
        f.write(key)
    print(name, "已记录")


def noneKeyDownloader(url, text, name):
    """存放未加密视频信息
    """
    global MSGSPATH
    msg = {
        'url': url,
        'text': text
    }
    msgFile = MSGSPATH + name.rsplit('.', 1)[0] + '.txt'
    with open(msgFile, 'w', encoding='utf-8') as f:
        json.dump(msg, f)
    print(name, "已记录")


def videoDownloader(url, name):
    """存放mp4视频信息
    """
    global MSGSPATH
    msg = {
        'url': url
    }
    msgFile = MSGSPATH + name.rsplit('.', 1)[0] + '.txt'
    with open(msgFile, 'w', encoding='utf-8') as f:
        json.dump(msg, f)
    print(name, "已记录")


class NameIntercapter:
    """拦截视频名
    """

    def __init__(self) -> None:
        super()

    def response(self, flow: mitmproxy.http.HTTPFlow):
        global VIDEONAME
        if re.match(r'^https://vod.study.163.com/eds/api/v1/vod/video\?videoId=(\d*?)&signature=(.*?)&clientType=1$', flow.request.url):
            VIDEONAME = json.loads(flow.response.text)['result']['name']


class FileIntercapter:
    """拦截加密文件
    """

    def __init__(self) -> None:
        super()

    def response(self, flow: mitmproxy.http.HTTPFlow):
        global FILE, URL
        if re.match(r'^https://jdvodluwytr3t.stu.126.net/nos/ept/hls/(.*?)\.m3u8\?ak=(.*?)&token=(.*?)key(.*?)token(.*?)t=(\d+?)$', flow.request.url):
            URL = flow.request.url
            FILE = flow.response.text


class NoneKeyIntercapter:
    """拦截未加密文件
    """

    def __init__(self) -> None:
        super()

    def response(self, flow: mitmproxy.http.HTTPFlow):
        global VIDEONAME
        if re.match(r'^https://jdvodluwytr3t.stu.126.net/nos/hls/(.*?).m3u8\?ak=(.*?)$', flow.request.url):
            threading.Thread(target=noneKeyDownloader, args=(
                flow.request.url, flow.response.text, VIDEONAME)).start()


class VideoIntercapter:
    """拦截mp4视频地址
    """

    def __init__(self) -> None:
        super()

    def request(self, flow: mitmproxy.http.HTTPFlow):
        global VIDEONAME
        if re.match(r'^https://jdvodluwytr3t.stu.126.net/nos/mp4/(.*?).mp4\?ak=(.*?)$', flow.request.url):
            threading.Thread(target=videoDownloader, args=(
                flow.request.url, VIDEONAME)).start()


class KeyIntercapter:
    """拦截解密key
    """

    def __init__(self) -> None:
        super()

    def response(self, flow: mitmproxy.http.HTTPFlow):
        global FILE, VIDEONAME, URL
        if re.match(r'^https://vod.study.163.com/eds/api/v1/vod/hls/key\?id=(\d*?)&token=(.*?)$', flow.request.url):
            if len(flow.response.content) == 16:
                threading.Thread(target=keyDownloader, args=(
                    URL, FILE, flow.response.content, VIDEONAME)).start()


# 加载拦截器
addons = [
    NameIntercapter(),
    FileIntercapter(),
    NoneKeyIntercapter(),
    VideoIntercapter(),
    KeyIntercapter()
]
