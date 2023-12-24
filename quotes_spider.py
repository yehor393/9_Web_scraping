import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.item import Item, Field


class QuoteItem(Item):
    quote = Field()
    author = Field()
    tags = Field()


class AuthorItem(Item):
    fullname = Field()
    born_date = Field()
    born_location = Field()
    description = Field()


async def parse_author(response, **kwargs):
    content = response.xpath("/html//div[@class='author-details']")
    fullname = content.xpath("h3[@class='author-title']/text()").get().strip()
    born_date = content.xpath("p/span[@class='author-born-date']/text()").get().strip()
    born_location = content.xpath("p/span[@class='author-born-location']/text()").get().strip()
    description = content.xpath("div[@class='author-description']/text()").get()
    if description:
        description = description.strip()
    yield AuthorItem(fullname=fullname, born_date=born_date, born_location=born_location, description=description)


class QuotesSpider(scrapy.Spider):
    name = "get_quotes"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com/"]
    custom_settings = {"ITEM_PIPELINES": {"data_pipeline.DataPipeline": 300}}

    def parse(self, response, **kwargs):
        for q in response.xpath("/html//div[@class='quote']"):
            quote = q.xpath("span[@class='text']/text()").get().strip()
            author = q.xpath("span/small[@class='author']/text()").get().strip()
            tags = [tag.strip() for tag in q.xpath("div[@class='tags']/a/text()").extract()]
            tags = [tag for tag in tags if tag]  # Remove empty tags
            yield QuoteItem(quote=quote, author=author, tags=tags)
            yield response.follow(url=self.start_urls[0] + q.xpath("span/a/@href").get(), callback=parse_author)

        next_link = response.xpath("/html//li[@class='next']/a/@href").get()
        if next_link:
            yield scrapy.Request(url=self.start_urls[0] + next_link)


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(QuotesSpider)
    process.start()
