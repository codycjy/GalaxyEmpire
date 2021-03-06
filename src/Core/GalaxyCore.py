import hashlib
import queue 
import json
import logging
import sys
from collections import defaultdict


import requests


salt = 'b6bd8a93c54cc404c80d5a6833ba12eb'

logging.basicConfig(level=logging.DEBUG,  # 控制台打印的日志级别
                    # filename='new.log',
                    # filemode='a',##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
                    # a是追加模式，默认如果不写的话，就是追加模式
                    format=
                    '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    # 日志格式
                    )
logging.getLogger("requests").setLevel(logging.WARNING)


def crypto(url, opt=''):
    opt_w = opt + salt
    data = opt + "&verifyKey=" + md5(url + opt_w)
    return data


def md5(parm):
    parm = str(parm)
    m = hashlib.md5()
    m.update(bytes(parm, 'utf-8'))
    return m.hexdigest()

def addArgs(args):
    ans=""
    for i in args.items():
        ans+='&'+str(i[0])+'='+str(i[1])
    return ans

headers = {
    'User-Agent': 'android',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
}

class GalaxyCore:
    
    fleetLevel = {
            20: defaultdict(int, {
                'ds': 2,
                'bs': 0,
                'de': 0,
                'cargo': 0
                }),
            25: defaultdict(int, {'ds': 10}),
            10: defaultdict(int, {
                'bs': 15,
                'cargo': 15
                }),
            12: defaultdict(int, {
                'bs': 40,
                'cargo': 30
                }),
            16: defaultdict(int, {
                'bs': 260,
                'cargo': 35
                }),
            88: defaultdict(int, {
                'cargo': 50,
                'bs': 50,
                'satellite': 200
                }),
            99: defaultdict(int, {'satellite': 2000})
            }


    ShipToID={  'ds':'ship214','de':'ship213','cargo':'ship203','bs':'ship207',
                'satellite':'ship210'}

    serverUrlList = {
            'ze': 'http://45.33.39.137/zadc/',
            'g1': 'http://45.33.44.248/yoox/',
            'g5': 'http://45.33.39.137/g5/',
            'g4': 'http://173.230.155.34/g4/',
            'g3': 'http://173.230.155.34/g3/',
            'g2': 'http://173.255.250.41/g2/',
            'yo': 'http://45.33.44.248/yoox/',
            'jd': 'http://173.255.250.41/jedi/',
            'at': 'http://45.33.39.137/zeat/',
            'dr': 'http://45.33.44.248/ddcc/',
            'co': 'http://45.33.44.248/ddcc/',
            'aq': 'http://173.230.155.34/carina/',
            'g6': 'http://45.33.44.248/g6/',
            'g7': 'http://173.255.250.41/g7/',
            'g8': 'http://45.33.44.248/g8/',
            'g10': 'http://45.33.39.137/g10/'
            }

    salt="b6bd8a93c54cc404c80d5a6833ba12eb"

    def __init__(self,username:str,password:str,server:str):
        self.username = username
        self.password = password
        self.server=server
        self.ppy_id=None
        self.ssid =None
        self.fleet=defaultdict(dict)
        self.planetIdDict=defaultdict(str)
        self.planet={}
        self.login()
    



    def _post(self,url:str,args:dict={})  -> dict:
        """
        Everything work with network start in this method
        """

        extra_args ={}
        if "login" not in url:
            extra_args=self.getSession()
        try:
            args.update(extra_args)
            url=self.serverUrlList[self.server]+url+addArgs(args)
        except KeyError:
            logging.warning("server wrong")
            sys.exit(0)
        logging.debug(url)
        try :
            req=requests.post(url,headers=headers,data=crypto(url))
            return {'status':0,'data':json.loads(req.text)}
        except Exception as e :
            logging.warning(e)
            return {'status':-1}

    def generateFleet(self,level):
        fleet={}
        for i in self.fleet[level].items():
            fleet[self.ShipToID[i[0]]]=i[1]
        return fleet
 
    def getSession(self): 
        "return session as dict"
        return {"sess_id":self.ssid,"ppy_id":self.ppy_id}

    def login(self):
        """
        Login and update session
        """

        url=    f'index.php?page=gamelogin&ver=0.1&tz=7&'\
                f'device_id=51dd0b0337f00c2e03c5bb110a56f818&device_name=OPPO&'\
                f'username={self.username}&password={md5(self.password)}'
        result=self._post(url,{1:1})
        if result['status'] == 0:
            loginResult=result['data']
        else:
            return{'status':-1,'data':result['data']}
        try:
            self.ppy_id=loginResult['ppy_id']
            self.ssid=loginResult['ssid']
        except KeyError:
            logging.warning("login failed")
            return {'status':-1}
        logging.info("Success")
        return {'status':0}

    def changePlanet(self, planetId)->dict:
        """
        change planet and return planet information.
        """

        url = f'game.php?page=buildings&mode='
        args={"cp":planetId}
        logging.info('changePlanet: ' +str(planetId))
        result=self._post(url,args)
        return result['data']


if __name__ == "__main__":
    g=GalaxyCore('username','password','ze')
    g.login()









