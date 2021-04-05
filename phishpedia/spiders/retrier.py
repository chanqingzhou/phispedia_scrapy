import os
import json
import base64
import scrapy
from scrapy_splash import SplashRequest
import pandas as pd
from urllib.parse import urlparse
import os
import socket
import websockets
import time
import json

script2 = """
function main(splash, args)
  assert(splash:go(splash.args.url))
  assert(splash:wait(3))
  local element = splash:select_all('*')
  local srcs = {}
  for _, img in ipairs(element) do
     local data = img.info()
     local new_data = {}
     new_data['nodeName'] = data.nodeName
     new_data['x'] = data.x
     new_data['y'] = data.y
     new_data['width'] = data.width
     new_data['height'] = data.height
     srcs[#srcs+1] = new_data
         
  end
  return {
    elements = srcs,
    html = splash:html(),
    png = splash:png{render_all=true},
    har = splash:har(),
    url = splash:url()
  }
end
"""

script = """
function main(splash, args)
  assert(splash:go(splash.args.url))
  assert(splash:wait(3))
  return {
    html = splash:html(),
    png = splash:png{render_all=true},
    har = splash:har(),
    url = splash:url()
  }
end
"""
class MyItem(scrapy.Item):
    # ... other item fields ...
    image_urls = scrapy.Field()
    images = scrapy.Field()
    file_path= scrapy.Field()

class ExtractSpider(scrapy.Spider):
    name = 'extract2'
    num = 0
    saveLocation = os.getcwd()

    custom_settings = {
        "ITEM_PIPELINES": {'phishpedia.pipelines.PhishPipeline': 300},
        "IMAGES_STORE": saveLocation,
        "IMAGES_EXPIRES": 0,
        "HTTPERROR_ALLOWED_CODES":[503]
    }

    def clean_domain(self, domain, deletechars='\/:*?"<>|'):
        for c in deletechars:
            domain = domain.replace(c, '')
        return domain

    def start_requests(self):
        df = pd.read_csv('D:/junyang/phispedia/phispedia_scrapy/phishpedia/spiders/retry.csv')
        counter = 0
        for i in range(len(df)):
            row = df.iloc[i]
            if (row['yes'] > 0 or row['unsure'] > 0 ) and row['no'] == 0:
                url = row['url']
                counter +=1
                continue
                splash_args = {
                    'lua_source': script,
                    'filters': 'fanboy-annoyance',
                    'timeout': 90,
                    'resource_timeout': 10

                }
                yield SplashRequest(url, self.parse_result, endpoint='execute', args=splash_args)
        print(counter)
    def parse_result(self, response):
       
        if response.status == 503:
            print(self.num)
            self.num += 1
            return
        else:
            self.num -= 1
            self.num = max(0, self.num)
            
        url = response.request._original_url
        domain = self.clean_domain(urlparse(response.data['url']).netloc, '\/:*?"<>|')

        png_bytes = base64.b64decode(response.data['png'])
        date_now = time.strftime("%Y-%m-%d", time.localtime(time.time()))

        output_folder = os.path.join('X:/', 'plausible_phishing')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        output_folder = os.path.join(output_folder, domain)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        screenshot_path = os.path.join(output_folder, "shot.png")
        info_path = os.path.join(output_folder, "info.txt")
        html_path = os.path.join(output_folder, "html.txt")
        lure_path = os.path.join(output_folder, "lure.txt")
        div_info = os.path.join(output_folder, "div.txt")
        
        with open(screenshot_path, 'wb+') as f:
            f.write(png_bytes)

        with open(html_path, 'wb+') as f:
            f.write(response.body)

        with open(info_path, 'w+') as f:
            f.write(response.data['url'])

        with open(lure_path, 'w+') as f:
            f.write(url)
        
        '''
        with open(div_info, 'w+') as f:
            ele_list = []
            for ele in response.data['elements'].values():
                f.write(ele['nodeName'] + '\t')
                f.write(str((float(ele['x']), float(ele['y']),
                                float(ele['x'] + ele['width']), float(ele['y'] + ele['height'])))+'\n')


        '''
    def url_join(self, urls, response):
        joined_urls = []
        for url in urls:
            joined_urls.append(response.urljoin(url))

        return joined_urls

# 600