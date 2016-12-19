import scrapy
import os


class QuotesSpider(scrapy.Spider):
    name = "crazy3dfree"
    download_dir = "SET_THIS"

    def start_requests(self):
        urls = [
            'http://www.crazy3dfree.com/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_top)

    def parse_top(self, response):
        # All categories are in directory Model and they are in <li> tags
        sel = scrapy.Selector(text=response.body, type="html")
        links = sel.xpath('//li//@href').extract()
        model_links = filter(lambda test: 'Model' in test, links)
        self.log("Crawled categories {}".format(model_links))

        for category in model_links:
            yield scrapy.Request(url=response.urljoin(category), callback=self.parse_category)

        with open("b", "wb") as f:
            f.write(str(model_links))

    def parse_category(self, response):
        # All results are in a table in a <li> so we will get all links in <li><table><td> hieararchy
        # This will generate more than all models but the next parser will ignore if it is not a leaf
        sel = scrapy.Selector(text=response.body, type="html")
        cells = sel.xpath('//li//td//@href').extract()
        for cell in cells:
            yield scrapy.Request(url=response.urljoin(cell), callback=self.parse_leaf)

        # We also need to follow links little bit
        next_page_selector = scrapy.Selector(text=response.body, type="html")
        next_page = sel.xpath('//td//li//a[contains(., "Next")]').extract()
        if next_page:
            next_page_link = scrapy.Selector(text=next_page[0], type="html").xpath("//@href").extract()[0]
            yield scrapy.Request(url=response.urljoin(next_page_link), callback=self.parse_category)

    def parse_leaf(self, response):
        sel = scrapy.Selector(text=response.body, type="html")
        download_link = sel.xpath('//td//a[contains(., "Download")]').extract()
        for dlink in download_link:
            # If the extension is rar/zip, download it
            file_links = scrapy.Selector(text=dlink, type="html").xpath('//@href').extract()
            for file_link in file_links:
                if file_link[-4:] == ".rar":
                    download_path = response.urljoin(file_link)
                    yield scrapy.Request(url=download_path, callback=self.save_file)

    # Opens the download link and downloads the assets into the specified folder
    def save_file(self, response):
        name = response.url.split('/')[-1]
        path = os.path.join(self.download_dir, name)
        with open(path, "wb") as f:
            f.write(response.body)
