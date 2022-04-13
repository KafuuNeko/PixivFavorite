# Pixiv爬虫
# 作者：KafuuNeko
# https://kafuu.cc/

from asyncio.windows_events import NULL
import sys
import requests
import json
import os
import time

# 校验Cookie是否有效


def getUserId(cookie):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063',
        'cookie': cookie
    }

    response = requests.get('https://www.pixiv.net/',
                            headers=headers, verify=False)
    try:
        return [True, response.headers['x-userid']]
    except Exception as ex:
        return [False, '']


# 获取指定ID所有图片文件，并下载
def downloadImages(saveDir, illustId, cookie):
    headers = {
        'Referer': 'https://www.pixiv.net/artworks/' + str(illustId),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063',
        'cookie': cookie}

    try:
        # illust 插图
        # manga 漫画
        url = 'https://www.pixiv.net/ajax/illust/' + \
            str(illustId) + '/pages?lang=zh'
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.encoding = 'utf-8'
        data = json.loads(response.text)

        if (data['error']):
            print('下载图片失败, illustId = ' + str(illustId))
            return

        for value in data['body']:
            # original 原图
            # regular 标准
            print('Downloading: ' + os.path.basename(value['urls']['regular']))

            saveFile = saveDir + '/' + \
                os.path.basename(value['urls']['regular'])

            if os.path.exists(saveFile) == False:
                imgres = requests.get(
                    value['urls']['original'], headers=headers, timeout=60, verify=False)
                with open(saveFile, "wb") as f:
                    f.write(imgres.content)
            else:
                print('[' + str(saveFile) + ']文件已存在')

    except Exception as ex:
        print(str(ex))
        print('下载图片失败, 正在重试。illustId = ' + str(illustId))
        time.sleep(5)
        downloadImages(saveDir, illustId, cookie)


# 下载收藏夹所有图片
def downloadFavorites(cookie, userId, saveDir, isHide):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063',
        'cookie': cookie}

    apiUrl = 'https://www.pixiv.net/ajax/user/' + \
        str(userId) + '/illusts/bookmarks'

    offset = 0
    inc = 50
    total = inc

    requests.adapters.DEFAULT_RETRIES = 5

    while (offset < total):
        try:
            rest = 'show'
            if isHide:
                rest = 'hide'
            url = apiUrl + '?tag=&offset=' + \
                str(offset) + '&limit=' + str(inc) + \
                '&rest=' + rest + '&lang=zh'

            print(url)

            response = requests.get(
                url, headers=headers, timeout=15, verify=False)
            response.encoding = 'utf-8'
            data = json.loads(response.text)

        except Exception as ex:
            print(str(ex))
            print('访问收藏信息失败，正在重试')
            time.sleep(5)
            continue

        if data['error']:
            print(data['message'])
            return

        offset = offset + inc

        body = data['body']
        total = body['total']

        for work in body['works']:
            print('Try downloading ' +
                  work['title'] + ', id=' + str(work['id']))
            downloadImages(saveDir, work['id'], cookie)


if __name__ == "__main__":
    if not os.path.exists('cookie.txt'):
        print('请将您的pixiv账户cookie保存到当前目录下的cookie.txt文件夹')
        sys.exit()

    cookie = str(open('cookie.txt').read())
    userId = getUserId(cookie)

    if not userId[0]:
        print('获取用户ID失败, 检查cookie是否有效')
        sys.exit()

    print('user_id: ' + userId[1])

    # 爬取公开收藏夹
    saveDir = 'images/' + str(userId) + '/public'
    if not os.path.exists(saveDir):
        os.makedirs(saveDir)
    downloadFavorites(cookie, userId, saveDir, False)

    # 爬取私有文件夹
    saveDir = 'images/' + str(userId) + '/private'
    if not os.path.exists(saveDir):
        os.makedirs(saveDir)
    downloadFavorites(cookie, userId, saveDir, True)
