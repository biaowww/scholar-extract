__author__ = 'peiyu'

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.http import Request
from scrapy.selector import Selector
from scholar.items import ScholarItem

class ScholarSpider(CrawlSpider):
    name = "scholar5"
    allowed_domains = ['wanfangdata.com.cn']
    url = "http://social.wanfangdata.com.cn/Scholar.aspx?q=%20%E5%8D%95%E4%BD%8D%3A%22%E5%8C%BB%E9%99%A2%22"
    start_urls = [url,]

    rules = [
            Rule(LinkExtractor(restrict_xpaths=('//div[@class="CoResearcherList"]/p/a'), unique=True), callback="parse_keyword", follow=False),
            Rule(LinkExtractor(restrict_xpaths=('//p[@class="pager_space"]'), unique=True), follow=True),  
    ]

    def parse_keyword(self,response):
        # print 'I am in parse_keyword!!!' + '+'*200
        hxs = Selector(response)
        item = ScholarItem()
        
        # parsing keyword information
        words = hxs.xpath('//div[@class="keyword_ul"]/li/a/text()').extract()
        all_word = u'|'.join(words)
        item['keyword'] = all_word

        coListURL = response.url.replace("Achievement.aspx", "CoResearcher.aspx")
        yield Request(url=coListURL, cookies={'PreferredCulture':'zh-CN'}, meta={'item':item}, callback=self.parse_coList)

    def parse_coList(self,response):
        # print 'I am in parse_coList!!!' + '+'*200
        hxs = Selector(response)
        item = ScholarItem(response.meta['item'])
        
        # parsing personal information
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
