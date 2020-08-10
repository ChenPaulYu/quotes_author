import scrapy
from scrapy import Request, FormRequest

class AuthorSpider(scrapy.Spider):
    name = 'author'
    start_url = 'http://quotes.toscrape.com/login'

    def start_requests(self):
        yield scrapy.Request(self.start_url, self.login)

        
    def login(self, response):
        csrf_token = response.xpath('//form/input[@name="csrf_token"]/@value').get()
        yield FormRequest.from_response(
            response, 
            formxpath ='//form',
            formdata  = {
                'csrf_token': csrf_token,
                'username'  : 'admin',
                'password'  : 'admin'
            },
            callback=self.parse
        )


    def parse(self, response):
        quotes = response.xpath('//div[@class="quote"]')
        for quote in quotes:
            link   = response.urljoin(quote.xpath('./span/a/@href').get())
            yield response.follow(link, callback=self.parse_item)
        
        next_page = response.xpath('//nav/ul/li[@class="next"]/a/@href').get()
        if next_page:
            page = next_page.split('/')[-2]
            print(f'============================={page}=============================')
            yield response.follow(next_page, callback=self.parse)

    def parse_item(self, response):

        author_detail = response.xpath('//div[@class="author-details"]')
        author = author_detail.xpath('./h3/text()').get().strip().strip('\n')
        date   = author_detail.xpath('./p/span[@class="author-born-date"]/text()').get()
        loc    = author_detail.xpath('./p/span[@class="author-born-location"]/text()').get().split('in')[-1].strip()
        desc   = author_detail.xpath('./div[@class="author-description"]/text()').get().strip().strip(u'\u201c\u201d') 

        yield {
            'author': author,
            'date'  : date  , 
            'loc'   : loc   ,
            'desc'  : desc
        }