# Pixiv爬虫
# 作者：KafuuNeko
# https://kafuu.cc/


import requests
import json
import os
import time
	

#校验Cookie是否有效
def checkCookie(cookie):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063',
        'cookie' : cookie}
    url = 'https://www.pixiv.net/tags/%E5%B0%91%E5%A5%B3/illustrations?p=30'
    while True:
        try:
            return requests.get(url, headers=headers, verify=False).url == url
        except Exception as ex:
            print(str(ex))
            print('Cookie校验失败, 正在重试')



#获取指定ID所有图片文件，并下载
def downloadImages(saveDir, illustId, cookie):
    headers = {
        'Referer': 'https://www.pixiv.net/artworks/' + str(illustId),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063',
        'cookie' : cookie}
    
    try:
        #illust 插图
        #manga 漫画
        url = 'https://www.pixiv.net/ajax/illust/' + str(illustId) + '/pages?lang=zh'
        response = requests.get(url, headers=headers, timeout = 10, verify=False)
        response.encoding = 'utf-8'
        data = json.loads(response.text)

        if (data['error']):
            print('下载图片失败, illustId = ' + str(illustId))
            return

        for value in data['body']:
            #original 原图
            #regular 标准
            print('Downloading: ' + os.path.basename(value['urls']['regular']))

            saveFile = saveDir + '/' + os.path.basename(value['urls']['regular'])

            if os.path.exists(saveFile) == False:
                imgres = requests.get(value['urls']['original'], headers=headers, timeout = 60, verify=False)
                with open(saveFile, "wb") as f:
                    f.write(imgres.content)
            else:
                print('[' + str(saveFile) + ']文件已存在')
                
    except Exception as ex:
        print(str(ex))
        print('下载图片失败, 正在重试。illustId = ' + str(illustId))
        time.sleep(5)
        downloadImages(saveDir, illustId, cookie)


#爬取
def crawlBookmarks(cookie, userId, saveDir, isHide):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063',
        'cookie' : cookie}

    apiUrl = 'https://www.pixiv.net/ajax/user/' + str(userId) + '/illusts/bookmarks'

    offset = 0
    inc = 50
    total = inc

    requests.adapters.DEFAULT_RETRIES = 5
    
    while (offset < total):
        try:
            rest = 'show'
            if isHide:
                rest = 'hide'
            url = apiUrl + '?tag=&offset=' + str(offset) + '&limit=' + str(inc) + '&rest=' + rest + '&lang=zh'
            
            print(url)

            response = requests.get(url, headers=headers, timeout = 15, verify=False)
            response.encoding = 'utf-8'
            data = json.loads(response.text)

        except Exception as ex:
            print(str(ex))
            print("访问收藏信息失败，正在重试")
            time.sleep(5)
            continue

        
        if data['error'] :
            print(data['message'])
            return

        offset = offset + inc
        
        body = data['body']
        total = body['total']

        for work in body['works'] :
            print('Try downloading ' + work['title'] + ', id=' + str(work['id']))
            downloadImages(saveDir, work['id'], cookie)
    

cookie = ''

if os.path.exists('cookie.txt'):
    cookie = str(open('cookie.txt').read())
    print("Cookie:" + cookie)
    checkCookie(cookie)
else:
    print("未检测到PixivCookie.txt文件")

userId = '51753240'


saveDir = 'images/' + str(userId) + '/public'
if not os.path.exists(saveDir) :
    os.makedirs(saveDir)
# crawlBookmarks(cookie, userId, saveDir, False)


saveDir = 'images/' + str(userId) + '/private'
if not os.path.exists(saveDir) :
    os.makedirs(saveDir)
crawlBookmarks(cookie, userId, saveDir, True)

