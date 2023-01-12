import hashlib
import json
import logging
import sys
import time
from collections import defaultdict
from arguments import SALT
import requests

from src.Logger.Logger import GalaxyLogger

def crypto(url, opt=''):
    opt_w = opt + SALT
    data = opt + "&verifyKey=" + md5(url + opt_w)
    return data


def md5(parm):
    parm = str(parm)
    m = hashlib.md5()
    m.update(bytes(parm, 'utf-8'))
    return m.hexdigest()


def addArgs(args):
    ans = ""
    for i in args.items():
        ans += '&' + str(i[0]) + '=' + str(i[1])
    return ans


headers = {
    'User-Agent': 'android',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
}


class GalaxyCore:
    fleet = {
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

    ShipToID = {'ds': 'ship214', 'de': 'ship213', 'cargo': 'ship203', 'bs': 'ship207',
                'satellite': 'ship210', 'lf': 'ship204', 'hf': 'ship205', 'cr': 'ship206',
                'dr': 'ship215', 'bomb': 'ship211', 'guard': 'ship216'}

    serverUrlList = {'g13': 'http://173.255.250.41/g13/',
                     'g12': 'http://173.230.155.34/g12/',
                     'g11': 'http://173.255.250.41/g11/',
                     'g10': 'http://45.33.39.137/g10/',
                     'g8': 'http://45.33.44.248/g8/',
                     'g9': 'http://173.255.250.41/g9/',
                     'g5': 'http://173.255.250.41/g5g7/',
                     'g7': 'http://173.255.250.41/g5g7/',
                     'g6': 'http://45.33.44.248/g4g6/',
                     'g4': 'http://45.33.44.248/g4g6/',
                     'g3': 'http://173.230.155.34/g2g3/',
                     'g2': 'http://173.230.155.34/g2g3/',
                     'g1': 'http://45.33.44.248/yoox/',
                     'yo': 'http://45.33.44.248/yoox/',
                     'je': 'http://173.230.155.34/jely/',
                     'ly': 'http://173.255.250.41/ge/',
                     'ze': 'http://45.33.39.137/zadc/',
                     'at': 'http://45.33.39.137/zadc/',
                     'dr': 'http://173.255.250.41/ge/',
                     'co': 'http://45.33.39.137/zadc/',
                     'de': 'http://45.33.39.137/zadc/',
                     'cy': 'http://45.33.39.137/zadc/',
                     'se': 'http://45.33.44.248/serpens/',
                     'sc': 'http://45.33.39.137/tmsc/',
                     'aq': 'http://173.230.155.34/carina/',
                     'ca': 'http://173.230.155.34/glge/',
                     'sa': 'http://45.33.39.137/tmsc/',
                     'ph': 'http://45.33.44.248/phoenix/',
                     'hl': 'http://173.255.250.41/hydra/',
                     'mu': 'http://45.33.39.137/tmsc/',
                     'tu': 'http://45.33.39.137/tmsc/',
                     'vo': 'http://45.33.39.137/tmsc/',
                     'do': 'http://45.33.39.137/tmsc/',
                     'cr': 'http://45.33.39.137/tmsc/',
                     'fo': 'http://173.230.155.34/glge/',
                     'ge': 'http://173.230.155.34/glge/',
                     'gl': 'http://173.230.155.34/glge/',
                     'el': 'http://173.230.155.34/ge/',
                     've': 'http://173.255.250.41/ge/',
                     'oc': 'http://173.230.155.34/ge/',
                     'ta': 'http://173.230.155.34/ge/',
                     'pi': 'http://173.230.155.34/ge/',
                     'bo': 'http://173.230.155.34/ge/',
                     'in': 'http://173.230.155.34/ge/',
                     'or': 'http://173.255.250.41/ge/',
                     'ar': 'http://173.255.250.41/ge/',
                     'ap': 'http://173.255.250.41/ge/',
                     'gr': 'http://173.255.250.41/ge/',
                     'ce': 'http://173.255.250.41/ge/',
                     'pa': 'http://173.255.250.41/ge/',
                     'vi': 'http://173.255.250.41/ge/',
                     'le': 'http://173.255.250.41/ge/'
                     }

    SALT = "b6bd8a93c54cc404c80d5a6833ba12eb"

    def __init__(self):
        self.username = None
        self.password = None
        self.server = None
        self.ppy_id = None
        self.ssid = None
        self.planetIdDict = defaultdict(str)
        self.planet = {}
        self.proxies = {
            'http': None,
            'https': None
        }
        self.coreType = 0  # 0: galaxy core, 1: galaxy node
        self.loggingPrefix = ''

    def getAccount(self, username, password, server):
        self.username = username
        self.password = password
        self.server = server


    def setLogger(self, logger:GalaxyLogger|None,level=logging.INFO):
        if logger:
            self.logger = logger
        else:
            self.logger= GalaxyLogger('./logs/',level=level,name=f'{self.username}@{self.server}')

    def startup(self):
        self.login()

    def _post(self, url: str, args={}) -> dict:
        """
        Everything work with network start in this method
        """

        if args is None:
            args = {}
        extra_args = {}
        if "login" not in url:
            extra_args = self.getSession()
        try:
            args.update(extra_args)
            serverUrl=self.serverUrlList.get(self.server,None)
            if serverUrl is None:
                raise InvalidServer(self.server)

            url =serverUrl + url + addArgs(args)
        except InvalidServer as e:
            self.logger.error(e)
            self.logger.critical("exiting...")
            sys.exit(0)

        try:
            self.logger.log(5, "POST: " + url)
            req = requests.post(url, headers=headers, data=crypto(url), proxies=self.proxies)
            data = json.loads(req.text)
            self.logger.log(5, f"RESPONSE:  {data}")
            if data['status'] != 'error':
                return {'status': 0, 'data': data}
            else:
                if data['err_code'] == 111:
                    self.logger.info(f"session expired, relogin")
                    self.login()
                    return self._post(url, args)
                try:
                    self.logger.warning(data['err_msg'])
                    return {'status': -1, 'err_msg': data['err_msg'], 'err_code': data['err_code']}
                except KeyError:
                    self.logger.error(data)
                    return {'status': -1}
        except json.JSONDecodeError as e:
            self.logger.warning(f"JSONDecodeError {e}" )
            return {'status': -1, 'err_msg': 'JSONDecodeError'}
        except WindowsError as e:
            if e.winerror == 10054:
                self.logger.warning("ConnectionResetError")
                return {'status': -1, 'err_msg': 'ConnectionResetError'}
            elif e.winerror == 10060:
                self.logger.warning("ConnectionTimeout")
                return {'status': -1, 'err_msg': 'ConnectionTimeout'}
            else:
                self.logger.warning(f"WindowsError {e}"  )
                return {'status': -1, 'err_msg': 'WindowsError'}
        except Exception as e:
            self.logger.error(e)
            return {'status': -1}
        except:
            self.logger.error("unknown error")
            return {'status': -1}

    def generateFleet(self, level):
        fleet = {}
        for i in self.fleet[level].items():
            fleet[self.ShipToID[i[0]]] = i[1]
        return fleet

    def getSession(self):
        """return session as dict"""
        return {"sess_id": self.ssid, "ppy_id": self.ppy_id}

    def login(self):
        """
        Login and update session
        """

        url = f'index.php?page=gamelogin&ver=0.1&tz=7&' \
              f'device_id=51dd0b0337f00c2e03c5bb110a56f818&device_name=OPPO&' \
              f'username={self.username}&password={md5(self.password)}'
        result = self._post(url, {1: 1})
        if result['status'] == 0:
            loginResult = result['data']
            self.logger.debug(loginResult)
        else:
            self.logger.info(result)
            return {'status': -1, 'err_msg': result.get('err_msg', 'login error')}
        try:
            self.ppy_id = loginResult['ppy_id']
            self.ssid = loginResult['ssid']
        except KeyError:
            self.logger.info("login failed")
            return {'status': -1, 'err_msg': 'Unknown error'}
        self.logger.info("Login Success")
        return {'status': 0}

    def changePlanet(self, planetId):
        """
        change planet and return planet information.
        """
        self.login()
        url = f'game.php?page=buildings&mode='
        args = {"cp": planetId}
        self.logger.info('changePlanet: ' + str(planetId))
        result = self._post(url, args)
        if result['status'] == 0:
            data = result.get('data')
            if data:
                return data
        try:
            self.logger.warning(result['err_msg'])
        except KeyError:  
            self.logger.warning(result)
        finally:
            self.logger.warning("changePlanet failed, sleep 15s and retry")
            time.sleep(15)
            return self.changePlanet(planetId)


class InvalidServer(Exception):
    def __init__(self,server,message="Invalid server"):
        self.server=server
        self.message=f"{message} {server} "
        super().__init__(self.message)


if __name__ == "__main__":
    pass
