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


class ExtractSpider(scrapy.Spider):
    name = 'of_extract'
    num = 0
    saveLocation = os.getcwd()

    custom_settings = {
        "ITEM_PIPELINES": {'phishpedia.pipelines.PhishPipeline': 300},
        "IMAGES_STORE": saveLocation,
        "IMAGES_EXPIRES": 0,
        "HTTPERROR_ALLOWED_CODES": [503]
    }

    def clean_domain(self, domain, deletechars='\/:*?"<>|'):
        for c in deletechars:
            domain = domain.replace(c, '')
        return domain

    def start_requests(self):
        file_path = 'D:/ruofan/git_space/phishpedia/benchmark/DatabaseJun13-Sep30'
        for folder in os.listdir(file_path):
            act_path = os.path.join(file_path, folder)
            info_path = os.path.join(act_path, 'info.txt')
            with open(info_path) as f:
                info = eval(f.read())
            url = info['url'].strip()



            output_log = os.path.join("X:/", 'of.txt')
            with open(output_log, 'a+') as f:
                f.write(url + '\n')
            splash_args = {
                'lua_source': script,
                'filters': 'fanboy-annoyance',
                'timeout': 90,
                'resource_timeout': 10

            }
            yield SplashRequest(url, self.parse_result, endpoint='execute', args=splash_args)

    def parse_result(self, response):

        url = response.request._original_url
        domain = self.clean_domain(urlparse(response.data['url']).netloc, '\/:*?"<>|')

        png_bytes = base64.b64decode(response.data['png'])
        date_now = time.strftime("%Y-%m-%d", time.localtime(time.time()))

        output_folder = os.path.join("X:/", 'of')
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