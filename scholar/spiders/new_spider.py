__author__ = 'peiyu'

import urllib
import codecs
from scrapy.contrib.spiders.init import InitSpider
from scrapy.http import Request, FormRequest
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import Rule
from scholar.items import ScholarItem
from scrapy.selector import HtmlXPathSelector

from scrapy.http.cookies import CookieJar

def convert(content):
    """convert GBK to utf-8"""
    those = []
    for this in content:
        that = this.decode("GBK")
        that = that.encode("utf-8")
        those.append(that)
    return those

def web_address(words):
    """convert keyword to web address content"""
    Address_name =[]
    for word in words:
        web_word = urllib.quote(word)
        Address_name.append(web_word)
    return Address_name

#f = codecs.open('C:/work/wanfang/test.txt','r','GBK')
f = codecs.open('names.txt','r', 'utf-8')
s = f.readlines()
f.close()
for line in s:
    test_name = line
    #print test_name
    #test_name1 = convert(test_name)
    test_name1 = "".join(test_name)
    test_name2 = web_address(test_name1.encode('utf-8'))
    #print test_name2


class ScholarSpider(InitSpider):
    name = "scholar4"
    allowed_domains = []
    Our_url = "http://social.wanfangdata.com.cn/Scholar.aspx?q="+"".join(test_name2)+"%20%E5%8D%95%E4%BD%8D%3A%22%E5%8C%BB%E9%99%A2%22"
    start_urls = [
        Our_url
    ]
    num = 1
    #rules = [
    #    Rule(SgmlLinkExtractor(restrict_xpaths=('//p[@pager_space]/a@href')), callback="parse_home", follow=True),
    #]

    def init_request(self):
        """This function is called before crawling starts."""
        return Request(url=self.Our_url, cookies={'PreferredCulture':'zh-CN'}, callback=self.parse_home)

    def parse_home(self, response):
        self.log("Fetch search page: %s" % response.url)
        hxs = HtmlXPathSelector(response)
        items = []

        item = ScholarItem()
        groups = hxs.select('//div[@class="CoResearcherList"]')
        next_page = hxs.select('//p[@class="pager_space"]/a')
        next_page_link = u""
        for link in next_page:
            if link.select('t/text()').extract() == []:
                pass
            elif link.select('t/text()').extract()[0] == u'\u4e0b\u4e00\u9875':
                next_page_link = link.select('@href').extract()

        item['scholars']=[]
        item['urlID']=[]
        item['institute']=[]
        for group in groups:
            scholar_name = group.select('p/a[@href]/text()').extract()
            scholar_url = group.select('p/a/@href').extract()
            danwei = group.select('p[2]/text()').extract()
            item['scholars'].append(scholar_name)
            item['urlID'].append(scholar_url)
            item['institute'].append(danwei)
            #print scholar_name
        yield item

        filename = "test"+str(self.num)+".htm"
        html_content = response.body
        #print html_content
        #html_content = convert([html_content,])[0]
        open(filename, 'wb').write(html_content)

        self.num += 1

        tmp="".join(next_page_link)
        req = Request(url="http://social.wanfangdata.com.cn/Scholar.aspx"+tmp, cookies={'PreferredCulture':'zh-CN'}, callback=self.parse_home)
        yield req










