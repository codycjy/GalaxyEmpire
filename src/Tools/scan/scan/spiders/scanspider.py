import scrapy
from scrapy.http import FormRequest
import json
import hashlib

salt = 'b6bd8a93c54cc404c80d5a6833ba12eb'


def crypto(url, opt=''):
    opt_w = opt + salt
    data = opt + "&verifyKey=" + md5(url + opt_w)
    return data


def md5(parm):
    parm = str(parm)
    m = hashlib.md5()
    m.update(bytes(parm, 'utf-8'))
    return m.hexdigest()


class ScanSpider(scrapy.Spider):
    name = 'scan'
    username = "CloudY"
    password = "Fuck741"
    server_url = "http://45.33.39.137/zadc/"
    login_url = f'index.php?page=gamelogin&ver=0.1&tz=7&' \
                f'device_id=51dd0b0337c00c2e03c5bb110a56f818&device_name=OPPO&' \
                f'username={username}&password={md5(password)}'
    galaxy, system = 1, 1
    url = f'http://45.33.39.137/zadc/game.php?page=galaxy&mode=2&galaxy={galaxy}&system={system}'
    start_urls = [url]
    def __init__(self,**kwargs):
        super(ScanSpider, self).__init__(**kwargs)
        self.kwargs=kwargs
        self.server=kwargs.get('server')
        self.server_url=self.kwargs.get('server_url')
        self.username=self.kwargs.get('username')
        self.password=self.kwargs.get('password')


    def start_requests(self):
        url = self.server_url + self.login_url
        yield FormRequest(url, method='post', body=crypto(url), callback=self.parse_login)

    def parse_login(self, response):
        user = (json.loads(response.body))
        ppy_id = user['ppy_id']
        ssid = user['ssid']
        self.start_urls.clear()
        for i in range(1, 2):
            for j in range(2 - i % 2, 151 - i % 2, 2):
                url = self.server_url+f'game.php?page=galaxy&mode=2&galaxy={j}&system={i}'
                self.start_urls.append(url)
        # i, j = 1, 1
        # self.url = f'http://45.33.39.137/zadc/game.php?page=galaxy&mode=2&galaxy={j}&system={i}'
        # self.start_urls.append(self.url)

        for i in self.start_urls:
            cookie={'sess_id':ssid,'ppy_id':ppy_id}
            yield scrapy.Request(i,cookies=cookie, callback=self.parse_galaxy, method='POST',)

    def parse_galaxy(self, response):
        data = json.loads(response.body)
        if data['status'] != 'ok':
            self.logger.warning(f'{data["status"]}')
            return
        if 'planets' in data['result'][0].keys():
            for i in data['result'][0]['planets'].values():
                planet_info = {'position': i['position'], 'name': i['name'], 'username': i['username']}
                if i['has_derbis']:
                    planet_info['derbis_metal'] = i['derbis']['metal']
                    planet_info['derbis_crystal'] = i['derbis']['crystal']
                else:
                    planet_info['derbis_metal'] = 0
                    planet_info['derbis_crystal'] = 0
                yield planet_info
