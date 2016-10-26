import scrapy
import os.path

class All3DFreeSpider(scrapy.Spider):
    name = 'all3dfree'
    download_dir = '/home/mrowca/crawler/all3dfree/downloads/'
    total_number_of_assets = 0

    # Opens each of the specified websites
    def start_requests(self):
        urls = [
                'http://www.all3dfree.net/--tv-panel.html',
                'http://www.all3dfree.net/--wall-panel1.html',
                'http://www.all3dfree.net/--sofa.html',
                'http://www.all3dfree.net/--chair.html',
                'http://www.all3dfree.net/--coffee-table.html',
                'http://www.all3dfree.net/--bed.html',
                'http://www.all3dfree.net/---doors.html',
                'http://www.all3dfree.net/---windows.html',
                'http://www.all3dfree.net/---cabinets.html',
                'http://www.all3dfree.net/bathroom.html',
                'http://www.all3dfree.net/office-furniture.html',
                'http://www.all3dfree.net/curtain.html',
                'http://www.all3dfree.net/kitchen.html',
                'http://www.all3dfree.net/decoration.html',
                'http://www.all3dfree.net/lamps.html',
                'http://www.all3dfree.net/electronics.html',
                'http://www.all3dfree.net/fashion-products.html',
                'http://www.all3dfree.net/equipments.html',
                'http://www.all3dfree.net/plants.html',
                'http://www.all3dfree.net/foods--drinks.html',
                'http://www.all3dfree.net/3d-characters.html',
                'http://www.all3dfree.net/transportation.html',
                'http://www.all3dfree.net/animals.html',
                'http://www.all3dfree.net/structure.html',
                'http://www.all3dfree.net/buildings.html',
                'http://www.all3dfree.net/manager-room-00-page.html',
                'http://www.all3dfree.net/general-office-00-page.html',
                'http://www.all3dfree.net/meeting-room-00-page.html',
                'http://www.all3dfree.net/office-resting-area-00-page.html',
                'http://www.all3dfree.net/function-hall-00-page.html',
                'http://www.all3dfree.net/leisure-club-00-page.html'
                ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_top_level)

    # Parses the top level website
    def parse_top_level(self, response):
        # Check if there are more pages (0,1,2,3,...) linked for this category on this page
        next_pages = response.xpath('//td[contains(@class,"wsite-multicol-col")]/div[contains(@class,"paragraph")]/font').css('a::attr(href)').extract()[1:]

        if not next_pages:
            print 'NO NEXT PAGES'
        else:
            print(str(len(next_pages)) + ' NEXT PAGES')

        # Find the assets on this page
        yield scrapy.Request(url=response.url, callback=self.parse_mid_level, dont_filter=True)

        # Find the assets on the next pages
        for page in next_pages:
            yield scrapy.Request(url=response.urljoin(page), callback=self.parse_mid_level)

    # Determines the link to each individual asset and opens them
    def parse_mid_level(self, response):
        print('MID_LEVEL ' + response.url)
        
        # Find all assets on website
        all_assets = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "galleryInnerImageHolder", " "))]').css('a::attr(href)').extract()[:]

        if not all_assets:
            print 'NO ASSETS'
        else:
            print(str(len(all_assets)) + ' ASSETS')
            self.total_number_of_assets += len(all_assets)
            print self.total_number_of_assets
        
        # Parse the individual assets websites
        for asset in all_assets:
            yield scrapy.Request(url=response.urljoin(asset), callback=self.parse)
    
    # Finds the download link for each individual asset and opens it
    def parse(self, response):
        
        # Orange link download
        downloads = response.xpath('//a[contains(text(), "Free Download")]').css('a::attr(href)').extract()[:]

        # Grey button download
        if not downloads:
            downloads = response.xpath('//a[contains(@class, "wsite-button")]').css('a::attr(href)').extract()[:]

        if not downloads:
            print 'NO DOWNLOADS'
        else:
            print(str(len(downloads)) + ' DOWNLOADS')
        
        # Download asset
        for download in downloads:
            yield scrapy.Request(url=response.urljoin(download), callback=self.save_file)

    # Opens the download link and downloads the assets into the specified folder
    def save_file(self, response):	
        name = response.url.split('/')[-1]
	path = os.path.join(self.download_dir, name)
        with open(path, "wb") as f:
            f.write(response.body)
            print(path)

    def get_path(self, url):
        return self.download_dir + url
