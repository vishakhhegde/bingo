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

    # rules = [Rule(LinkExtractor(), callback='parse_filter_link', follow=True)]

    def parse_link(self, response):
        # is_product_page = response.css('div.product-image-container > div.product-primary-image > a::attr(href)')
        # check_women = response.xpath('//*[@id="main"]/div[1]/ol/li[2]/a/span/text()').extract_first()
        # check_top = response.xpath('//*[@id="main"]/div[1]/ol/li[3]/a/span/text()').extract_first()
        # if is_product_page and check_women=='WOMENS' and check_top=='TOPS':
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
        print(len(search_results))
        for i, product in enumerate(search_results):
            link = process_link(
                product.css('div.product-tile-name > a.name-link::attr(href)').extract_first())
            yield scrapy.Request(url=link, callback=self.parse_link)
        
        link_to_next = response.css('a.pagination-item-link.pagination-item-link-next::attr(href)').extract_first()
        if link_to_next:
            yield scrapy.Request(url=link_to_next, callback=self.parse)