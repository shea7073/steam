import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule, Request
import os
import json
import re
import pymongo
from pymongo import MongoClient

class TopSellersSpider(CrawlSpider):
    name = "top_sellers"
    allowed_domains = ["store.steampowered.com"]

    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'

    def start_requests(self):
        yield scrapy.Request(url="https://store.steampowered.com/search/?filter=topsellers&page=1&count=100",
                             headers={'User-Agent': self.user_agent})

    rules = (
        Rule(LinkExtractor(restrict_xpaths="//div[@id='search_resultsRows']/a"), callback="parse_item", follow=True,
             process_request='set_headers'),)

    def set_headers(self, request, spider):
        request.headers['User-Agent'] = self.user_agent
        request.cookies['lastagecheckage'] = '1-0-1995'
        request.cookies['birthtime'] = 786258001
        return request

    def parse_item(self, response):
        tags = []
        yield {
            'Title': response.xpath("//div[@id='appHubAppName_responsive']/text()").get(),
            'Text_Rating': response.xpath("//span[contains(@class, 'game_review_summary')][1]/text()").get(),
            'Percent_Rating': response.xpath("//span[contains(@class, 'responsive_reviewdesc')][1]/text()").get(),
            'Release_Date': response.xpath("//div[@class='date']/text()").get(),
            'Price_No_Sale': response.xpath("//div[@class='game_purchase_price price'][1]/text()").get(),
            'Price_Sale': {"Original_Price": response.xpath("//div[@class='discount_original_price'][1]/text()").get(),
                           "Sale_Price": response.xpath("//div[@class='discount_final_price'][1]/text()").get()},
            'Image_Link': response.xpath("//img[@class='game_header_image_full']/@src").get(),
            'Tags': response.xpath("//a[@class='app_tag']/text()").getall()

        }


process = CrawlerProcess(settings={
        "FEEDS": {
            "output.json": {"format": "json"},
        },
    })


def clean_data(file_name):

    client = MongoClient('mongodb+srv://sean:bu_final@cluster0.pvuhuo1.mongodb.net/?retryWrites=true&w=majority')
    db = client['Steam_Data']
    collection = db['Top_Games']

    with open(file_name, encoding='utf-8') as f:
        data = json.load(f)
    for row in data:
        for key in row.keys():
            if type(row[key]) == str:
                row[key] = re.sub(r"[\n\t\r]*", "", row[key])
            if type(row[key]) == list:
                for i in range(0, len(row[key])):
                    row[key][i] = re.sub(r"[\n\t\r]*", "", row[key][i])
        collection.insert_one(row)


def scrape():
    if os.path.exists("output.json"):
        os.remove("output.json")
    process.crawl(TopSellersSpider)
    process.start()
    clean_data('output.json')


if __name__ == '__main__':
    scrape()
