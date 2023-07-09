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
    special_server= {
        "aq":
        {
            "galaxy":{
                "start": 1,
                "end": 10
            },
            "system":{
                "start": 1,
                "end": 400,
            },
            "step": 1,
        },
        "g10":
        {
            "galaxy":{
                "start": 1,
                "end": 152,
            },
            "system":{
                "start": 1,
                "end": 60,
            },
            "step": 2,
        }
    }

    old_server_list=["aq"]

    def __init__(self, **kwargs):
        super(ScanSpider, self).__init__(**kwargs)
        self.kwargs = kwargs
        self.server:str = kwargs.get('server','')
        self.server_url:str = self.kwargs.get('server_url','')
        self.username = self.kwargs.get('username')
        self.password = self.kwargs.get('password')
        self.logger.info(f'server:{self.server},username:{self.username},password:{self.password},server_url:{self.server_url}')
        self.old_flag=self.server in self.old_server_list
        self.special_flag=self.server in self.special_server.keys()

        if self.server_url == '':
            raise Exception('server_url is empty')

    def start_requests(self):
        self.login_url = f'index.php?page=gamelogin&ver=0.1&tz=7&' \
                         f'device_id=51dd0b0337c00c2e03c5bb110a56f818&device_name=OPPO&' \
                         f'username={self.username}&password={md5(self.password)}'
        url = self.server_url + self.login_url
        yield FormRequest(url, method='post', body=crypto(url), callback=self.parse_login)

    def parse_login(self, response):
        user = (json.loads(response.body))
        ppy_id = user['ppy_id']
        ssid = user['ssid']
        self.start_urls.clear()
        self.logger.info(f"old_flag:{self.old_flag},special_flag:{self.special_flag}")
        if not self.special_flag:
            for i in range(1, 51):
                for j in range(2 - i % 2, 151 - i % 2, 2):
                    url = self.server_url + f'game.php?page=galaxy&mode=2&galaxy={j}&system={i}'
                    self.start_urls.append(url)
        else:
            self.logger.warning(f'special server {self.server}')
            for i in range(1,self.special_server[self.server]['galaxy']['end']+1):
                for j in range(2-i % 2 ,self.special_server[self.server]['system']['end']+1,self.special_server[self.server]['step']):
                    url=self.server_url+f'game.php?page=galaxy&mode={1 if self.old_flag else 2}&galaxy={i}&system={j}'
                    self.start_urls.append(url)


        for i in self.start_urls:
            cookie = {'sess_id': ssid, 'ppy_id': ppy_id}
            yield scrapy.Request(i, cookies=cookie, callback=self.parse_galaxy, method='POST', )

    def parse_galaxy(self, response):
        data = json.loads(response.body)
        if data['status'] != 'ok':
            self.logger.warning(f'{data["status"]}')
            return
        if self.old_flag:
            data=data['result']
        else:
            data=data['result'][0]

        if 'planets' in data.keys() and not self.old_flag:
            for i in data['planets'].values():
                planet_info = {'position': i['position'], 'name': i['name'], 'username': i['username']}
                if i['has_derbis']:
                    planet_info['derbis_metal'] = i['derbis']['metal']
                    planet_info['derbis_crystal'] = i['derbis']['crystal']
                else:
                    planet_info['derbis_metal'] = 0
                    planet_info['derbis_crystal'] = 0
                if i['ally_name']:
                    planet_info['has_ally'] = 1
                    planet_info['ally_name'] = i['ally_name']
                else:
                    planet_info['has_ally'] = 0
                    planet_info['ally_name'] = ''
                yield planet_info
        elif 'planets' in data.keys() and self.old_flag:
            for j in data['planets'].items():
                if int(j[0])>30:
                    continue
                i=j[1]
                planet_info = {'position': i['position'], 'name': i['name'], 'username': i['username']}
                if 'derbis' in i and i['derbis']:
                    planet_info['derbis_metal'] = i['derbis']['metal'].replace(',','')
                    planet_info['derbis_crystal'] = i['derbis']['crystal'].replace(',','')
                else:
                    planet_info['derbis_metal'] = 0
                    planet_info['derbis_crystal'] = 0
                if 'ally_name' in i and i['ally_name']:
                    planet_info['has_ally'] = 1
                    planet_info['ally_name'] = i['ally_name']
                else:
                    planet_info['has_ally'] = 0
                    planet_info['ally_name'] = ''
                yield planet_info

