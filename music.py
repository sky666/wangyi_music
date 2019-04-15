# -*- coding:utf-8 -*-
import requests
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import jieba
from lxml import etree


# requests的headers头信息
headers = {
    'Referer': 'http://music.163.com',
    'Host': 'music.163.com',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
}


# 定义一个函数，返回某一首歌的歌词
def get_song_lyric(lyric_url):
    res = requests.get(lyric_url, headers=headers)
    if 'lrc' in res.json():    # 歌词是 json 数据
        lyric = res.json()['lrc']['lyric']
        new_lyric = re.sub(r'[\d:.[\]]', '', lyric)  # 使用正则表达式去除时间信息
        return new_lyric
    else:
        return ''


# 去除停用词
def move_stop_words(f):
    stop_words = ['作词', '作曲', '编曲', 'Arranger', '录音', '混音', '人声', 'Vocal', '弦乐', 'Keyboard', '键盘', '编辑', '助理',
                  'Assistants', 'Mixing', 'Editing', 'Recording', '音乐', '制作', 'Producer', '发行', 'produced', 'and',
                  'distributed']
    for stop_word in stop_words:
        f = f.replace(stop_word, '')
    return f


# 生成词云
def create_word_cloud(f):
    print('生成词云')
    f = move_stop_words(f)
    text = ' '.join(jieba.cut(f, cut_all=False, HMM=True))
    wc = WordCloud(
        font_path='./SimHei.ttf',  # 设置中文字体,字体放在当前程序目录下
        max_words=100,  # 设置最大的字数
        width=2000,  # 设置画布的宽度
        height=1200,  # 设置画布的高度
    )
    wordcloud = wc.generate(text)
    # 写词云图片
    wordcloud.to_file('wordcloud.jpg')
    # 显示词云文件
    plt.imshow(wordcloud)
    plt.axis('off')
    plt.show()


# 得到指定歌手页面热门前 50 的歌曲 ID, 歌曲名
def get_songs(artist_id):
    page_url = 'https://music.163.com/artist?id=' + artist_id
    # 获取网页 HTML
    res = requests.get(page_url, headers=headers)
    # 用Xpath 解析前 50 首热门歌曲
    html = etree.HTML(res.text)
    href_xpath = "//*[@id='hotsong-list']//a/@href"
    name_xpath = "//*[@id='hotsong-list']//a/text()"
    hrefs = html.xpath(href_xpath)
    names = html.xpath(name_xpath)
    # 设置热门歌曲的 ID, 歌曲名称
    song_ids = []
    song_names = []
    for href, name in zip(hrefs, names):
        song_ids.append(href[9:])
        song_names.append(name)
    return song_ids, song_names


def main():
    # 设置歌手 ID, 周杰伦 ID 为 6452
    artist_id = input('请输入歌手 ID：')
    [song_ids, song_names] = get_songs(artist_id)
    # 所有歌词
    all_word = ''
    # 获取每首歌歌词
    for (song_id, song_name) in zip(song_ids, song_names):
        # 歌词API url
        lyric_url = 'http://music.163.com/api/song/lyric?os=pc&id=' + song_id + '&lv=-1&kv=-1&tv=-1'  # 需要找到 API 接口
        lyric = get_song_lyric(lyric_url)
        all_word = all_word + ' ' + lyric
        print(song_name)  # 歌曲名

    create_word_cloud(all_word)  # 生成词云


if __name__ == '__main__':
    main()
