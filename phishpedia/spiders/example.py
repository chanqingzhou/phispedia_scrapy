
import json
import base64
import scrapy
from scrapy_splash import SplashRequest
import pandas as pd
from urllib.parse import urlparse
import os
script = """
    function main(splash)
        assert(splash:go(splash.args.url))
        assert(splash:wait(3))
        return {png=splash:png{render_all=true},
                html=splash:html()
                }
    end
    """


class ExtractSpider(scrapy.Spider):
    name = 'extract'
    num = 1

    def clean_domain(self, domain, deletechars = '\/:*?"<>|'):
        for c in deletechars:
            domain = domain.replace(c, '')
        return domain


    def start_requests(self):
        df = pd.read_csv('test.csv',delimiter = '\t')
        df.columns = ['date','url','c']
        for url in df['url']:
            splash_args = {
                'lua_source':script,

            }
            yield SplashRequest(url, self.parse_result, endpoint='execute', args=splash_args)

    def parse_result(self, response):

        url = response.url
        domain = self.clean_domain(urlparse(url).netloc, '\/:*?"<>|')
        output_folder = os.path.join('results', domain)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        screenshot_path = os.path.join(output_folder, "shot.png")
        info_path = os.path.join(output_folder, "info.txt")
        html_path = os.path.join(output_folder, "html.txt")

        png_bytes = base64.b64decode(response.data['png'])

        with open(screenshot_path, 'wb+') as f:
            f.write(png_bytes)

        with open(html_path, 'wb+') as f :
            f.write(response.body)

        with open(info_path, 'w+') as f :
            f.write(url)

#600