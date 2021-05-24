# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose

def process_title(title):
    return title.replace('\n', '')

def process_price(price):
    return float(price.replace('\n', '').replace('$', ''))

def process_photo_url(url):
    return 'https:' + url

def process_link(link):
    product_id = link.split('/')[-1]
    return f'https://us.boohoo.com/pd/{product_id}'

def process_product_id(link):
    product_id = link.split('/')[-1].split('.')[0]
    return product_id

class BoohooItem(scrapy.Item):
    product_id = scrapy.Field(input_processor=MapCompose(process_product_id))
    title = scrapy.Field(input_processor=MapCompose(process_title))
    link = scrapy.Field(input_processor=MapCompose(process_link))
    price = scrapy.Field(input_processor=MapCompose(process_price))
    photo_url = scrapy.Field(input_processor=MapCompose(process_photo_url))

