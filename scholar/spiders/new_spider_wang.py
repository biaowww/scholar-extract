__author__ = 'peiyu'

import urllib
from scrapy.http import Request
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scholar.items import ScholarItem
from scrapy.selector import Selector
from scrapy.http.cookies import CookieJar

def web_address(word):
    """convert keyword to web address content"""
    return urllib.quote(word)

class ScholarSpider(CrawlSpider):
    name = "scholar5"
    allowed_domains = []
    url = "http://social.wanfangdata.com.cn/Scholar.aspx?q=%20%E5%8D%95%E4%BD%8D%3A%22%E5%8C%BB%E9%99%A2%22"
    start_urls = [url,]
    num = 1

    rules = [
            Rule(LinkExtractor(restrict_xpaths=('//p[@class="pager_space"]'), unique=True), callback="parse_home", follow=True),  
    ]

    def parse_home(self, response):
        self.log("Fetch search page: %s" % response.url)
        hxs = Selector(response)

        # get links for scholors
        groups = hxs.xpath('//div[@class="CoResearcherList"]')

        scholarsCoList = []
        scholarsKeyword = []
        for group in groups:
            scholar_url = group.xpath('p/a/@href').extract()
            scholarsCoList.append("".join(scholar_url).replace("Achievement.aspx","CoResearcher.aspx"))
            scholarsKeyword.append("".join(scholar_url))

        for surl in scholarsCoList:
            yield Request(url=surl, cookies={'PreferredCulture':'zh-CN'}, callback=self.parse_coList)

        for kurl in scholarsKeyword:
            yield Request(url=kurl, cookies={'PreferredCulture':'zh-CN'}, callback=self.parse_keyword)

    def parse_coList(self,response):
        hxs = Selector(response)
        # parsing personal information
        item = ScholarItem()
        head = hxs.xpath('//div[@class="head_list"]')
        item['Scholars'] = head.xpath("h1/a/text()").extract()
        item['UrlID'] = head.xpath("h1/a/@href").extract()
        item['Institute'] = head.xpath('p[@class="Organization_p"]/text()').extract()
        zzz = head.xpath('p[@class="font_5"]/text()').extract()
        item['Papers'] = str(zzz[1])
        item['Cites'] = str(zzz[2])
        item['HIndex'] = str(zzz[3])

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
        yield item

    def parse_keyword(self,response):
        hxs = Selector(response)
        item = ScholarItem()
        # parsing keyword information
        words = hxs.xpath('//div[@class="keyword_ul"]/li/a/text()').extract()
        for word in words:
            item['keyword'].append(u'|'.join(word))
        yield item














