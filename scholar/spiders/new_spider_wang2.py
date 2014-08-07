__author__ = 'peiyu'



import urllib
import codecs
import re

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.http import Request
from scrapy.selector import Selector
from scholar.items import ScholarItem
from scrapy.http.cookies import CookieJar

def web_address(word):
    """convert keyword to web address content"""
    return urllib.quote(word)

class ScholarSpider(CrawlSpider):
    name = "scholar6"
    allowed_domains = ['wanfangdata.com.cn']
    url = "http://social.wanfangdata.com.cn/Scholar.aspx?q=%20%E5%8D%95%E4%BD%8D%3A%22%E5%8C%BB%E9%99%A2%22"
    start_urls = [url,]
    artileID = set()

    rules = [
            Rule(LinkExtractor(restrict_xpaths=('//p[@class="pager_space"]'), unique=True), callback="parse_home", follow=True),  
    ]

    def parse_home(self, response):
        self.log("Fetch search page: %s" % response.url)
        hxs = Selector(response)
        item = ScholarItem()

        # get a link for next page
        next_page = hxs.xpath('//p[@class="pager_space"]/a')
        next_page_link = u""
        for link in next_page:
            if link.xpath('t/text()').extract() == []:
                pass
            elif link.xpath('t/text()').extract()[0] == u'\u4e0b\u4e00\u9875':
                next_page_link = link.xpath('@href').extract()

        # get links for scholors
        groups = hxs.xpath('//div[@class="CoResearcherList"]')

        scholarsCoList = []
        scholarsKeyword = []
        for group in groups:
            scholar_url = group.xpath('p/a/@href').extract()
            scholarsCoList.append("".join(scholar_url).replace("Achievement.aspx","CoResearcher.aspx"))
            scholarsKeyword.append("".join(scholar_url))


        for surl in scholarsCoList:
            m = re.search("\?(.*)",surl)
            if m.group(1) in self.artileID:
                pass
            else:
                request = Request(url=surl, cookies={'PreferredCulture':'zh-CN'}, callback=self.parse_coList)
                request.meta['item'] = item
                yield request
                self.artileID.add(m.group(1))

        tmp="".join(next_page_link)
        request = Request(url="http://social.wanfangdata.com.cn/Scholar.aspx"+tmp, cookies={'PreferredCulture':'zh-CN'}, callback=self.parse_home)
        request.meta['item'] = item
        yield request


    def parse_coList(self,response):
        hxs = Selector(response)
        # parsing personal information
        item = ScholarItem(response.meta['item'])

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


        keywordURL = response.url.replace("CoResearcher.aspx","Achievement.aspx")
        #print keywordURL
        request = Request(url=keywordURL, cookies={'PreferredCulture':'zh-CN'}, callback=self.parse_keyword)
        request.meta['item'] = item
        yield request

        #yield item

    def parse_keyword(self,response):
        hxs = Selector(response)
        item = ScholarItem(response.meta['item'])
        # parsing keyword information
        words = hxs.xpath('//div[@class="keyword_ul"]/li/a/text()').extract()
        all_word = u'|'.join(words)
        item['keyword'] = all_word
        yield item
















