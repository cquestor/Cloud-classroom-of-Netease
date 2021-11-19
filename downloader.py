import os
import re
import json
import requests
from Crypto.Cipher import AES


MSGSPATH = "./msgs/"  # 信息存储文件，注意末尾的'/'不能少
KEYSPATH = "./keys/"  # key存放文件，注意末尾的'/'不能少
OUTPATH = "./videos/"  # 视频下载地址，注意末尾的'/'不能少
MSGFILES = []
KEYFILES = []


headers = {
    'Connection': "keep-alive",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
}


# 加载信息文件
for each in os.listdir(MSGSPATH):
    MSGFILES.append(each)

# 加载密钥文件
for each in os.listdir(KEYSPATH):
    KEYFILES.append(each)

for each in MSGFILES:
    videoName = OUTPATH + each.rsplit('.', 1)[0] + '.mp4'
    msg = json.loads(open(MSGSPATH + each, 'r').read())
    # 判断是否为mp4视频
    if 'text' not in msg.keys() and each not in KEYFILES:
        print(videoName + "    MP4视频    下载中...", end="   ")
        response = requests.get(msg['url'], headers=headers)
        with open(videoName, "wb") as f:
            f.write(response.content)
        print("完成")
    # 判断是否为加密文件
    elif 'url' in msg.keys() and each in KEYFILES:
        print(videoName + "    加密视频    下载中...", end="   ")
        key = open(KEYSPATH + each, "rb").read()
        cryptor = AES.new(key, AES.MODE_CBC, key)
        baseUrl = msg['url'].split('?', 1)[0].replace(
            ".m3u8", "").rsplit("/", 1)[0] + "/"
        with open(videoName, 'wb+') as f:
            for ts_url in re.findall(r'\d*?_.*?_.*?.ts', msg['text']):
                ts_url = baseUrl + ts_url
                response = requests.get(ts_url, headers=headers)
                f.write(cryptor.decrypt(response.content))
        print("完成")
    # 未加密文件
    else:
        print(videoName + "    未加密视频    下载中...", end="   ")
        baseUrl = msg['url'].split('?', 1)[0].replace(
            ".m3u8", "").rsplit("/", 1)[0] + "/"
        with open(videoName, 'wb+') as f:
            for ts_url in re.findall(r'\d*?_.*?_.*?.ts', msg['text']):
                ts_url = baseUrl + ts_url
                response = requests.get(ts_url, headers=headers)
                f.write(response.content)
        print("完成")
