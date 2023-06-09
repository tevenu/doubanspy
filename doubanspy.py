import os
import re
import time
import requests
from bs4 import BeautifulSoup
import random
from write import write_dict_to_csv
useragent = "useragent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
            "Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.57"


# 随机生成user-agent
def get_ua():
    first_num = random.randint(55, 76)
    third_num = random.randint(0, 3800)
    fourth_num = random.randint(0, 140)
    os_type = [
        '(Windows NT 6.1; WOW64)', '(Windows NT 10.0; WOW64)', '(X11; Linux x86_64)',
        '(Macintosh; Intel Mac OS X 10_14_5)'
    ]
    chrome_version = 'Chrome/{}.0.{}.{}'.format(first_num, third_num, fourth_num)

    ua = ' '.join(['Mozilla/5.0', random.choice(os_type), 'AppleWebKit/537.36',
                   '(KHTML, like Gecko)', chrome_version, 'Safari/537.36']
                  )
    return ua


# 获取电影连接
def get_links(url):
    ua = get_ua()
    headers = {'User-Agent': ua}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'html.parser')
        elements = soup.find_all(attrs={'class': 'hd'})
        links = []
        for element in elements:
            href = element.a['href']
            links.append(href)
    except Exception as e:
        print(e)
    return links


def getfilminfo(url):
    ua = get_ua()
    headers = {'User-Agent': ua}
    filminfo = []
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'html.parser')
    # 片名
    name = soup.find(attrs={'property': 'v:itemreviewed'}).text.split(' ')[0]
    # 上映年份
    year = soup.find(attrs={'class': 'year'}).text.replace('(', '').replace(')', '')
    # 评分
    score = soup.find(attrs={'property': 'v:average'}).text
    # 评价人数
    votes = soup.find(attrs={'property': 'v:votes'}).text
    infos = soup.find(attrs={'id': 'info'}).text.split('\n')[1:11]
    # 导演
    director = infos[0].split(': ')[1]
    # 编剧
    scriptwriter = infos[1].split(': ')[1]
    # 主演
    actor = infos[2].split(': ')[1]
    # 类型
    filmtype = infos[3].split(': ')[1]
    # 国家/地区
    area = infos[4].split(': ')[1]
    if '.' in area:
        area = infos[5].split(': ')[1].split(' / ')[0]
        # 语言
        language = infos[6].split(': ')[1].split(' / ')[0]
    else:
        area = infos[4].split(': ')[1].split(' / ')[0]
        # 语言
        language = infos[5].split(': ')[1].split(' / ')[0]

    if '大陆' in area or '香港' in area or '台湾' in area:
        area = '中国'
    if '戛纳' in area:
        area = '法国'
    # 时长
    times0 = soup.find(attrs={'property': 'v:runtime'}).text
    times = re.findall('\d+', times0)[0]
    filminfo.append(name)
    filminfo.append(year)
    filminfo.append(score)
    filminfo.append(votes)
    filminfo.append(director)
    filminfo.append(scriptwriter)
    filminfo.append(actor)
    filminfo.append(filmtype)
    filminfo.append(area)
    filminfo.append(language)
    filminfo.append(times)
    filepath = 'TOP250.xlsx'
    # insert2excel(filepath, filminfo)


def getinfo(url):
    ua = get_ua()
    headers = {'User-Agent': ua}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    r.encoding = 'utf-8'
    info = {}
    soup = BeautifulSoup(r.text, 'html.parser')
    info["片名"] = soup.find(attrs={'property': 'v:itemreviewed'}).text.split(' ')[0]
    info["上映年份"] = soup.find(attrs={'class': 'year'}).text.replace('(', '').replace(')', '')
    info["评分"] = soup.find(attrs={'property': 'v:average'}).text
    info["评价人数"] = soup.find(attrs={'property': 'v:votes'}).text
    infos = soup.find(attrs={'id': 'info'}).text.split('\n')[1:11]
    info["导演"] = infos[0].split(': ')[1]
    info["编剧"] = infos[1].split(': ')[1]
    info["主演"] = infos[2].split(': ')[1]
    info["类型"] = infos[3].split(': ')[1]
    info["制片国家/地区"] = infos[4].split(': ')[1]
    info["语言"] = infos[5].split(': ')[1]
    info["上映日期"] = infos[6].split(': ')[1]
    info["片长"] = infos[7].split(': ')[1]
    return info


def get_comment(url):
    ua = get_ua()
    headers = {'User-Agent': ua}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'html.parser')
    # 获取电影名
    movie_name = soup.find('h1').text.split(" ")[0]
    # 存储电影评论的字典
    comment = {"电影名": movie_name}
    comment_items = soup.find_all(attrs={'class': 'comment-item'})
    for item in comment_items:
        comment_info_span = item.find_all('span', class_='comment-info')
        target_span = comment_info_span[0].find_all('span')[1]
        comment["评价"] = target_span.get('title')
        comment["label"] = 1 if comment["评价"] in ['力荐', '推荐'] else 0
        comment["短评"] = item.find(attrs={'class': 'short'}).text
        write_dict_to_csv(comment, '测试.csv')
    print(f"完成电影{movie_name}")



def main():
    for i in range(11):
        print(f'正在爬取第{i + 1}页,请稍等...')
        url = 'https://movie.douban.com/top250?start={}&filter='.format(i * 25)
        links = get_links(url)
        for link in links:
            # 获取电影信息
            # info = getinfo(link)
            # write_dict_to_csv(info, 'movie.csv')
            # time.sleep(random.uniform(3, 5))
            # 获取好评
            good_comment_url = link + "comments?percent_type=h&start=150&limit=150&status=P&sort=new_score"
            get_comment(good_comment_url)
            time.sleep(random.uniform(3, 5))
            # 获取差评
            # bad_comment_url = link + "comments?percent_type=l&limit=100&status=P&sort=new_score"
            # get_comment(bad_comment_url)
            # time.sleep(random.uniform(3, 5))




if __name__ == "__main__":
    main()
