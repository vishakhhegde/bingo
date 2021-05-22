import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from boohoo.items import BoohooItem, process_link


class ProductSpider(scrapy.Spider):
    name = 'boohoo_crawl_spider'
    allowed_domains = ['us.boohoo.com']
    start_urls = ['https://us.boohoo.com/womens/tops']

    def parse_link(self, response):
        product_loader = ItemLoader(item=BoohooItem(),
                                    selector=response)
        product_loader.add_css('photo_url', 'div.product-image-container > div.product-primary-image > a::attr(href)')
        product_loader.add_css('title', 'div.product-col-2 > h1.product-name::text')
        product_loader.add_value('link', response.url)
        product_loader.add_css('price', 'div.product-price > span.price-sales::text')
        product_loader.default_output_processor = TakeFirst()
        yield product_loader.load_item()

    def parse(self, response):
        search_results = response.css('div.product-tile')
        for i, product in enumerate(search_results):
            link = process_link(
                product.css('div.product-tile-name > a.name-link::attr(href)').extract_first())
            yield scrapy.Request(url=link, callback=self.parse_link)
        
        link_to_next = response.css('a.pagination-item-link.pagination-item-link-next::attr(href)').extract_first()
        if link_to_next:
            yield scrapy.Request(url=link_to_next, callback=self.parse)