import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from spainicbc.items import Article


class SpainicbcSpider(scrapy.Spider):
    name = 'spainicbc'
    start_urls = ['http://spain.icbc.com.cn/icbc/%e6%b5%b7%e5%a4%96%e5%88%86%e8%a1%8c/%e8%a5%bf%e7%8f%ad%e7%89%99%e7%bd%91%e7%ab%99/en/Announcement/default.htm']

    def parse(self, response):
        links = response.xpath('//a[@class="data-collecting-sign text2"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('(//div[@align="right"]//a[@class="text2"])[last()]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        date = response.xpath("//*[(@id = 'InfoPickFromFieldControl')]/text()").get()

        title = response.xpath('//div[@class="H1"]//text()').getall()
        title = [text.strip() for text in title if text.strip()]
        if title:
            title = title[0]

        content = response.xpath('//td[@id="mypagehtmlcontent"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
