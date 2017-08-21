#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import requests
from lxml import etree
from functools import lru_cache


@lru_cache()
def get_requests_cookies(url):
    '''
    缓存 cookies
    :param url:
    :return:
    '''
    s = requests.Session()
    return s.get(url).cookies


def bing_image_search_by_requests(word, num=5):
    '''
    根据搜索页面，分析出的图片数据
    :param word:
    :param num:
    :return:
    '''
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
               'Cache-Control': 'no-cache',
               'Connection': 'keep-alive',
               'Host': 'cn.bing.com',
               'Pragma': 'no-cache',
               'Referer': 'http://cn.bing.com/images/search?q=%s' % word,
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'}
    s = requests.Session()
    s.headers.update(headers)
    #
    # # @FIXME 先进行一次请求，保存cookies信息，保证搜索页的响应正常，直接请求搜索页无效，cookies可进行缓存重复使用，提高效率
    url = 'http://cn.bing.com'
    # r = s.get(url)

    cookies = get_requests_cookies(url)

    url = 'http://cn.bing.com/images/search?q=%s' % word

    content = s.get(url, cookies=cookies).content.decode('utf-8')

    dom_tree = etree.HTML(content)
    images = dom_tree.xpath("//div[@class='img_cont hoff']/img/@src | //div[@class='img_cont hoff']/img/@data-src")

    # @FIXME 过滤掉非URL元素，页面存在图片base64的情况，为慢加载的Img标签纯色背景图，所以过滤掉
    images = [image for image in images if image.find("http") != -1]

    return images[:num]


def translate_english(word):
    '''
    根据英文单词查字典
    '''
    html = requests.get('http://dict.cn/' + word).content.decode('utf-8')
    ##获取网页代码

    audio_base_url = 'http://audio.dict.cn/'

    dom_tree = etree.HTML(html)

    phonetic = dom_tree.xpath("//bdo[@lang='EN-US']")
    cixing = dom_tree.xpath("//ul[@class='dict-basic-ul']/li/span/text()")
    zh_word = dom_tree.xpath("//ul[@class='dict-basic-ul']/li/strong/text()")
    us_pronunciation = dom_tree.xpath("//i[@class='sound']/@naudio")
    uk_pronunciation = dom_tree.xpath("//i[@class='sound fsound']/@naudio")

    data = {}

    data['word'] = word

    if (len(phonetic) == 0):
        data['uk-phonetic'] = ''
        data['us-phonetic'] = ''
    else:
        data['uk-phonetic'] = phonetic[0].text
        data['us-phonetic'] = phonetic[1].text

    data['explains'] = cixing
    data['translation'] = zh_word

    data['pronunciation'] = []

    us_pronunciation.extend(uk_pronunciation)

    for pronunciation in us_pronunciation:
        data['pronunciation'].append('%s%s' % (audio_base_url, pronunciation))

    return data
