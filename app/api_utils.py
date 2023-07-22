import re
from urllib.parse import urlsplit
import urllib.robotparser as urp
from bs4 import BeautifulSoup
import cchardet
import requests as req


#RULES: No object instantiation in this file, too expensive

def url_is_valid(input: str):
    #Validate URL first...
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex, input)

def can_scrape(url: str, rp):
    #Get robot URL
    url_parts = urlsplit(url)
    base_url = url_parts.scheme + "://" + url_parts.netloc
    robot_url = base_url + '/robots.txt'
    print(base_url)
    rp.set_url(robot_url)
    rp.read()
    return rp.can_fetch("*", url)

def get_articles(feed: str):
    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    res = req.get(feed, headers=header)
    soup = BeautifulSoup(res.content, features='lxml')
    articles = soup.findAll('item')
    return articles