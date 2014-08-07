# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class ScholarItem(Item):
    # define the fields for your item here like:
    # name = Field()
    #pass
    Scholars = Field()
    UrlID = Field()
    Institute = Field()
    Papers = Field()
    Cites = Field()
    HIndex = Field()
    Tutor = Field()
    CoResearchers = Field()
    keyword = Field()


