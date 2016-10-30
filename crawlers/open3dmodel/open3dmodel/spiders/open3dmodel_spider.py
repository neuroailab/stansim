import scrapy
import os

class open3dmodelSpider(scrapy.Spider):
    name = "open3dmodel"
    download_dir = '/home/chengxuz/ThreeDworld_related/download_open3dmodel/'
    saved_dict  = {} # dict to store the downloaded files

    # Start pages
    def start_requests(self):
        urls = [
            'http://open3dmodel.com/download/file/3ds/page/1',
            'http://open3dmodel.com/download/file/gsm/page/1',
            'http://open3dmodel.com/download/file/obj/page/1',
            'http://open3dmodel.com/download/file/c4d/page/1',
            'http://open3dmodel.com/download/file/max/page/1',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_page)

    # Parse the top-level page
    def parse_page(self, response):
        print("Page " + response.url)

        if unicode(response.url[-1], 'utf-8').isnumeric():
            folder  = response.url.split('/')[-3]
        else:
            folder  = response.url.split('/')[-1]

        all_assets = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "labels-single", " "))]').css('a::attr(href)').extract()[:]
        next_pages = response.xpath('//*[contains(concat( " ", @rel, " " ), concat( " ", "next", " "))]').css('a::attr(href)').extract()[:]
        print("Len " + str(len(all_assets)))
        #print(all_assets[0])

        for every_object in all_assets:
            yield scrapy.Request(url=every_object, callback=lambda res:self.parse_item(res, folder)) 

        if len(next_pages)>0:
            print("Next page: " + next_pages[0])
            yield scrapy.Request(url=next_pages[0], callback=self.parse_page)

    # Parse the item-level page
    def parse_item(self, response, folder):

        old_url     = response.url
        name = old_url.split('/')[-1]
        name = folder + '/' + name.split('.')[0] + '.zip'

        if name in self.saved_dict:
            return
        self.saved_dict[name] = True

        down_links  = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "downloadlink", " "))]').css('a::attr(href)').extract()[:]
        for down_link in down_links:
            print("Download Link " + str(down_link))
            yield scrapy.Request(url= 'http://open3dmodel.com' + down_link, callback=lambda res,name=name:self.save_file(res, name))

    # Save the file
    def save_file(self, response, name):	
	path = os.path.join(self.download_dir, name)
        with open(path, "wb") as f:
            f.write(response.body)
            print(path)
