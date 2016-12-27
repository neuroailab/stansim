import subprocess
import os
import time
import numpy as np
import bs4
import re
import json

#to obtain crawlera API key, follow instructions here: https://doc.scrapinghub.com/crawlera.html
KEY = os.environ['CRAWLERA_API_KEY']

def get_models(i):
    """will get 3d models on page i 
          model data in zip file
          model metadata stored in .json file
    """
    linkurl = "http://archibaseplanet.com/gdl?category=0&page=%d" % (24 * i + 1)
    topath = 'links_%d.html' % i
    os.system('wget "%s" -O %s' % (linkurl, topath))
    
    soup = bs4.BeautifulSoup(open(topath))

    model_base = 'http://www.archibaseplanet.com/download/count'
    data_base = 'http://www.archibaseplanet.com/download'

    model_hrefs = [model_base + '/' + x.findAll('a')[1].attrs['href'].split('/')[-1] for x in soup.findAll('table', 'preview-pad')[0].findAll('td')]
    data_hrefs = [data_base + '/' + x.findAll('a')[1].attrs['href'].split('/')[-1] for x in soup.findAll('table', 'preview-pad')[0].findAll('td')]

    print(model_hrefs)
    
    reg = re.compile('location: ([\S]+)')

    for h, d in zip(model_hrefs, data_hrefs):
        hs = h.split('/')[-1].split('.')[0]
        print(KEY, h, hs)
        #os.system("curl -vs -x  proxy.crawlera.com:8010 -U %s: %s &> /dev/stdout | tee -a %s.out" % (KEY, h, hs))
        os.system("curl -vs -x  proxy.crawlera.com:8010 -U %s: %s 2> %s.out" % (KEY, h, hs))
        #args = ['curl', '-vs', '-x', 'proxy.crawlera.com:8010', '-U', KEY + ':', h, '&>', '/dev/stdout', '|', 'tee', '-a', hs + '.out']
        #proc = subprocess.Popen(args)
        #proc.wait()

        s = open(hs + '.out', 'rU').read()
        url = reg.search(s).groups()[0]
        os.system('wget %s -O %s.zip' % (url, hs))
        time.sleep(np.random.randint(5))
        datapath = '%s_data.html' % hs
        os.system('wget %s -O %s' % (d, datapath))
        dsoup = bs4.BeautifulSoup(open(datapath))
        c1, c2 = dsoup.findAll('title')[0].text.split(' | ')
        name = c1.strip()
        cat = c2.strip().split('Category: ')[-1]
        tags = [a.text for a in dsoup.findAll('a') if 'gdl/tag/' in a.attrs['href']]
        data = {'category': cat, 'name': name, 'tags': tags}
        with open('%s.json' % hs, 'w') as _f:
            json.dump(data, _f)
        
import sys
if __name__ == '__main__':
    thing = int(sys.argv[1])
    get_models(thing)
