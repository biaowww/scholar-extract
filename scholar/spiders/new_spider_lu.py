# -*- coding: utf-8 -*-
__author__ = 'peiyu'

import urllib

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.http import Request

from scholar.items import ScholarItem

def web_address(word):
    """convert keyword to web address content"""
    return urllib.quote(word)

class ScholarSpider(CrawlSpider):
    name = "scholar3"
    allowed_domains = ['wanfangdata.com.cn']
    url = "http://social.wanfangdata.com.cn/Scholar.aspx?q=%20%E5%8D%95%E4%BD%8D%3A%22%E5%8C%BB%E9%99%A2%22"
    start_urls = [url,]
    # num = 1

    rules = [
            Rule(LinkExtractor(restrict_xpaths=('//p[@class="pager_space"]'), unique=True), callback="parse_home", follow=True),  
    ]

    
    def parse_home(self, response):
        # self.log("Fetch search page: %s" % response.url)
        hxs = Selector(response)

        # get links for scholors
        groups = hxs.xpath('//div[@class="CoResearcherList"]')

        for group in groups:
            item = ScholarItem()
            scholar_url = group.xpath('p/a/@href').extract()
            CoList_url = "".join(scholar_url).replace("Achievement.aspx","CoResearcher.aspx")
            Keyword_url = "".join(scholar_url)
            Request(url=CoList_url, callback=self.parse_coList)
            Request(url=Keyword_url, callback=self.parse_keyword)
            yield item

    def parse_coList(self, response):
        hxs = Selector(response)
        # parsing personal information
        print '+'*100
        head = hxs.xpath('//div[@class="head_list"]')
        item = response.meta["item"]
        item['Scholars'] = head.xpath("h1/a/text()").extract()
        item['UrlID'] = head.xpath("h1/a/@href").extract()
        item['Institute'] = head.xpath('p[@class="Organization_p"]/text()').extract()
        zzz = head.xpath('p[@class="font_5"]/text()').extract()
        item['Papers'] = str(zzz[0])
        item['Cites'] = str(zzz[1])
        item['HIndex'] = str(zzz[2])

        # parsing Tutor and CoResearchers
        content = hxs.xpath('//p[@class="font_1"]|//ul[@class="CoResearcherList"]')

        typ = None

        item["Tutor"] = []
        item["CoResearchers"] = []

        for cont in content:
            con = cont.extract()
            context = cont.xpath("text()").extract()[0]

            if u'\u5bfc\u5e08' == context:
                typ = "tutor"
            elif u'\u5408\u4f5c\u5b66\u8005' == context:
                typ = "co"
            elif u'CoResearcherList' in con:
                if typ == 'tutor':
                    url = cont.xpath('li/p/a/@href').extract()[0]
                    name = cont.xpath('li/p/a/text()').extract()[0]
                    item["Tutor"].append(u"|".join([name,url]))
                elif typ == "co":
                    url = cont.xpath('li/p/a/@href').extract()
                    name = cont.xpath('li/p/a/text()').extract()
                    item["CoResearchers"].append(u"|".join([name[0],name[1],url[0],url[1]]))
                else:
                    raise ValueError("typ is None.")

        item["Tutor"] = u"#".join(item["Tutor"])
        item["CoResearchers"] = u"#".join(item["CoResearchers"])

    def parse_keyword(self,response):
        print '-'*100
        hxs = Selector(response)
        item = ScholarItem(response.meta["item"])
        # parsing keyword information
        words = hxs.xpath('//div[@class="keyword_ul"]/li/a/text()').extract()
        for word in words:
            item['keyword'].append(u'|'.join(word))

