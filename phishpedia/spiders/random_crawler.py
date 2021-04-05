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
from scrapy.linkextractors import LinkExtractor

script = """
function main(splash, args)
  assert(splash:go(splash.args.url))
  assert(splash:wait(3))
  return {
    html = splash:html(),
    png = splash:png{height=1080, width=1920},
    url = splash:url()
  }
end
"""


class MyItem(scrapy.Item):
    # ... other item fields ...
    image_urls = scrapy.Field()
    images = scrapy.Field()
    file_path = scrapy.Field()


class ExtractSpider(scrapy.Spider):
    name = 'rand'
    num = 0
    saveLocation = os.getcwd()

    custom_settings = {
        "ITEM_PIPELINES": {'phishpedia.pipelines.PhishPipeline': 300},
        "IMAGES_STORE": saveLocation,
        "IMAGES_EXPIRES": 0,

    }

    def clean_domain(self, domain, deletechars='\/:*?"<>|'):
        for c in deletechars:
            domain = domain.replace(c, '')
        return domain

    def start_requests(self):
        with open('sample_urls.txt') as f:
            for i in f.readlines()[400:]:
                url = i.strip()
                domain = self.clean_domain(urlparse(url).netloc, '\/:*?"<>|')
                output_folder = "D:/junyang/ss_login"

                output_folder = os.path.join(output_folder, domain)
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                else:
                    if len(os.listdir(output_folder)) > 5:
                        print(output_folder)
                        print("done")
                        continue
                splash_args = {
                    'lua_source': script,
                    'filters': 'fanboy-annoyance',
                    'timeout': 90,
                    'resource_timeout': 10

                }
                time.sleep(8)
                yield SplashRequest(url, self.parse_result, endpoint='execute', args=splash_args,meta = {'output':output_folder})

    def parse_result(self, response):
        png_bytes = base64.b64decode(response.data['png'])
        output_folder = response.meta.get('output')
        screenshot_path = os.path.join(output_folder, "shot1.png")
        splash_args = {
            'lua_source': script,
            'filters': 'fanboy-annoyance',
            'timeout': 90,
            'resource_timeout': 10
        }
        with open(screenshot_path, 'wb+') as f:
            f.write(png_bytes)

        le = LinkExtractor()
        counter  = 2
        print(le.extract_links(response))
        for link in le.extract_links(response):
            if counter >11:
                break
            print(link.url)
            counter  += 1


            yield SplashRequest(link.url, self.parse_result2, endpoint='execute', args=splash_args,meta = {'counter':counter, 'output':output_folder})

    def parse_result2(self, response):


        png_bytes = base64.b64decode(response.data['png'])
        output_folder = response.meta.get('output')


        screenshot_path = os.path.join(output_folder, "shot{}.png".format(response.meta.get('counter')))
        with open(screenshot_path, 'wb+') as f:
            f.write(png_bytes)

    def url_join(self, urls, response):
        joined_urls = []
        for url in urls:
            joined_urls.append(response.urljoin(url))

        return joined_urls

# 600