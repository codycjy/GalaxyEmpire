import asyncio
import json
import logging
from collections import defaultdict
import time

import requests

from src.Core.GalaxyCore import GalaxyCore
from src.Core.Planet import Planet

logging.getLogger("requests").setLevel(logging.CRITICAL)
INF=1e18


def intTime():
    return int(time.time())

def showServerList() -> dict:  # seem useless presently
    """
    auto update server list
    :return: server list
    """
    url = "http://192.81.130.154/gc2_sl_google.php"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                      ' AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/80.0.3987.149 Safari/537.36'
    }
    result = requests.get(url, headers=headers,timeout=3)
    data = json.loads(result.text)
    server = {}
    for i in data['lists']:
        name = i['name']
        if ':' in name:
            name = name.split(':')[0]
        else:
            name = name[:2].lower()
        server[name] = i['url']
    return server


class Galaxy(GalaxyCore):
    def __init__(self):
        super().__init__()
        self.attackLevel = 0
        self.fleetOnPlanet = defaultdict(dict)
        self.resourcesOnPlanet = defaultdict()
        self.planetInDanger =  []
        self._planet = {}
        self.initialized = False
        self.info = defaultdict(dict)

    def escapeParamsInit(self):
        if not self.info['detectInterval']:
            self.info['detectInterval']=30
        if not self.info['escapeInAdvance']:
            self.info['escapeInAdvance']=60

    def getTasks(self, attackTargetList, attackLevel, exploreTargetList, exploreLevel, taskEnabled, fleetLevel=None):  # TODO: deprecated in the future
        self.attackLevel = attackLevel[0]
        self.attackTargetList = attackTargetList
        self.attackTimes = attackLevel[1]
        self.attackFrom = attackLevel[2]

        self.exploreLevel = exploreLevel[0]
        self.exploreTargetList = exploreTargetList
        self.exploreTimes = exploreLevel[1]
        self.exploreFrom = exploreLevel[2]

        self.isAttack = taskEnabled['attack']
        self.isExplore = taskEnabled['explore']
        self.isEscaping = taskEnabled['escape']

        self.fleet = fleetLevel if fleetLevel is not None else self.fleet
        self.escapeParamsInit()

    def getTaskNew(self, task: dict, coreType: int = 1):
        """
        get task from task generator
        """
        self.coreType = coreType
        self.username = task['meta']['username']
        self.password = task['meta']['password']
        self.server = task['meta']['server']
        self.loggingPrefix = f'[{self.username}@{self.server}] | '

        self.isAttack = task['enabled'].get('attack', False)
        self.isExplore = task['enabled'].get('explore', False)
        self.isEscaping = task['enabled'].get('escape', False)

        if self.isAttack:
            self.attackLevel = task['attack']['level']
            self.attackTargetList = list(
                map(lambda x: dict(zip(['galaxy', 'system', 'planet'], x)), task['attack']['target']))
            self.attackTimes = task['attack']['times']
            self.attackFrom = task['attack']['startFrom']

        if self.isExplore:
            self.exploreLevel = task['explore']['level']
            self.exploreTargetList = list(
                map(lambda x: dict(zip(['galaxy', 'system', 'planet'], x)), task['explore']['target']))
            self.exploreTimes = task['explore']['times']
            self.exploreFrom = task['explore']['startFrom']
        self.escapeParamsInit()

    def getInfo(self,**kwargs):
        for i in kwargs:
            self.info[i]=kwargs[i]

    def startup(self):
        if not self.logger:self.setLogger(logger=None)
        self.login()
        self.updateBuildingInfo()

    def taskCore(self, task):
        """
        all task based on task Core func including relogin
        0:relogin 1:attack&&explore 2:escape
        3:recall 4:runFunc
        """

        if task['type'] == 0:
            self.relogin()
            yield 0
        elif task['type'] == 1:
            waittime = 0
            self.changePlanet(task['from'])
            for _ in range(task['times']):
                result = self.Attack(task['target'], task['level'])
                waittime = max(result.get('waittime', 0), waittime)
            waittime = max(waittime, 0) + 30
            yield int(waittime)

        elif task['type'] == 2:
            yield self.escape(task['planetId'], task['enemyFleet'])
        elif task['type'] == 3:
            yield self.recallFleet(task['fleetId'])
        elif task['type'] == 4:
            yield task['func']()

    def relogin(self):
        """
        login and update
        """
        self.login()
        self.updateBuildingInfo()

    async def enableAutoLogin(self):
        """
        enable auto login
        """
        while True:
            await asyncio.sleep(900)
            next(self.taskCore({'type': 0}))

    def getAttackFleet(self, target, level):
        url = "game.php?page=my_fleet1"
        __args = {}
        __args.update(dict(zip(['type', 'mission'], [4, 15] if 50 < level < 100 else [1, 1])))
        if not self.fleet[level]:
            self.logger.warning("wrong task, will not attack")
            return {}
        else:
            __args.update(self.generateFleet(level))
            __args.update(target)

        result = self._post(url, __args)
        if result['status'] == 0:
            try:
                __args.update({'token': result['data']['result']['token']})
            except KeyError:
                pass
        else:
            raise Exception('Error while getAttackFleet')
        return __args

    def Attack(self, target, level):
        url = 'game.php?page=fleet3'
        additional_args = {'staytime': 1}
        __args = {}
        try:
            __args = self.getAttackFleet(target, level)
        except Exception as e:
            self.logger.warning(e)
            return {'status': -1, 'waittime': 0}

        self.logger.info(f'{"Attacking" if level<50 else "Exploring"} to {target}')  # need to distinguish attack and explore
        isFailed = True
        waitTime = 0
        if level > 50:
            __args.update(additional_args)

        result = self._post(url, __args)
        if result['status'] == 0:
            if result['data']['status'] == 'ok':
                self.logger.debug(result['data'])
                self.logger.info(f"{'Attack' if level<50 else 'Explore'} to {target} success")
                waitTime = (float(result['data']['result']['backtime'])) + 30
                isFailed = False

        self.logger.warning(f"{target} {'attack' if level<50 else 'explore'} failed")
        return {'waittime': waitTime if not isFailed else 0}

    def updateBuildingInfo(self):
        url = "game.php?page=buildings"
        result = self._post(url)
        if result['status'] == 0:
            buildInfo = result['data']
            self.planet.clear()
            for i in buildInfo['result']['buildInfo']['result']['Planets'].items():
                planet = (i[1]['galaxy'], i[1]['system'], i[1]['planet'], i[1]['planet_type'])
                self.planetIdDict[i[0]] = planet
                self.planetIdDict[planet] = i[0]
                planetInformation = self.getSession()
                planetInformation.update({'server': self.server, 'planetId': i[0], 'position': planet,
                                          'username': self.username, 'password': self.password})
                self.planet[i[0]] = Planet(planetInformation)
                self.planet[i[0]].setLogger(self.logger)

    def checkEnemy(self) -> None:
        """
        Check whether there is enemy attacking us
        Compare the old attack fleet and the new attack fleet, if they are the same, give up the escape
        If some attack fleet disapper,either cancel or finish the attack,
        call relative fleet back
        """
        self.updateBuildingInfo()

        url = "game.php?page=fleet&action=detected"
        result = self._post(url)
        if result['status'] != 0:
            return

        result = result['data']['result']  # attacking enemies
        if not result:
            self.logger.info("No enemy attacking us")

        self.logger.debug(f"raw attacking result: {result}")

        newPlanetInDanger = []
        planetInDanger= defaultdict(int)
        enemyFleet = {}

        for i in result:
            target = (i['endGalaxy'], i['endSystem'], i['endPlanet'], i['endType'])
            plannetId = self.planetIdDict[target]
            newPlanetInDanger.append(plannetId)
            enemyFleet[plannetId] = i['FleetList']
            self.info['arrivingTime'][plannetId] = min(int(i['endTime']), self.info['arrivingTime'].get(plannetId, INF))
            planetInDanger[plannetId] += 1

        self.info['enemyFleet'] .update(enemyFleet)
        planetNotInDanger,addedPlanetInDanger = [],[]
        for i in self.planetInDanger:
            if i not in newPlanetInDanger:
                planetNotInDanger.append(i)

        for i in newPlanetInDanger:
            if i not in self.planetInDanger:
                addedPlanetInDanger.append(i)
        self.planetInDanger = newPlanetInDanger

        if planetNotInDanger or addedPlanetInDanger:
            self.logger.info(f"Planet no longer in danger: {planetNotInDanger}")
            self.logger.info(f"Planet in danger: {addedPlanetInDanger}")



        recalledFleet = []
        noArrivingTime = []

        for i in planetNotInDanger:
            self.logger.info(f"Planet {i} no longer in danger, cancel escape")
            if self.info['enableRecall'] != 0:
                self.recallEscape(self.info['escapingFleetID'][i])
                recalledFleet.append(i)
            else:
                self.logger.info(f"Recall disabled, will not recall")

            noArrivingTime.append(i)
        for i in noArrivingTime:
            self.info['arrivingTime'].pop(i)
        # when enemy will arrive with in 60 seconds, escape
        for i in self.info['arrivingTime'].items():
            if 0 < i[1]-intTime() < self.info['escapeInAdvance']:
                if self.info['escapingFleetID'].get(i[0],-1) == -1 :  # or 1 just fot test
                    self.logger.info(f" {i[0]} will be attacked in {i[1]-intTime()} seconds, escape")
                    result = next(self.taskCore({'type': 2, 'planetId': i[0], 'enemyFleet': self.info['enemyFleet'][i[0]]}))
                    if result == 0:
                        self.logger.warning(f"{i[0]} Escape failed")
                        return
                    self.logger.info(f"{i[0]} escape success.  Fleet id: {result}")
                    self.info['escapingFleetID'][i[0]] = result
                else:
                    self.logger.info(f"{i[0]} will be attacked in {i[1]-intTime()} seconds, already escaping")
            elif i[1]-intTime() < 0:
                self.logger.info(f" {i[0]} will be attacked in {i[1]-intTime()} seconds, already attacked")
                noArrivingTime.append(i[0])


            if i[1]==INF:
                self.info['arrivingTime'].pop(i[0])

        for i in recalledFleet:
            self.info['escapingFleetID'].pop(i)




    def recallFleet(self, fleetId: int):
        """
        recall fleet
        :param fleetId: fleet id

        :return:
        """
        url = "game.php?page=fleet&action=sendfleetback"
        __args = {'fleetID': fleetId}
        result = self._post(url, __args)
        if result['status'] == 0:
            self.logger.info(f'{fleetId} Recall success')
            return 0
        else:
            self.logger.warning(f'{fleetId}Recall failed')
            return 1


    def recallEscape(self, fleetId):
        """
        recall the escape fleet
        :param fleetId:
        :return:
        """
        next(self.taskCore({'type': 3, 'fleetId': fleetId}))


    def escape(self, planetId: str, enemyFleet):
        """
        escape from planet
        :return escape fleet id
        """
        __args = {}
        planet = self.planet[planetId]
        next(self.taskCore({"type":4,"func":planet.updateResources}))
        __args.update(planet.getFleet())
        __args.update({'mission': 4})
        self.logger.info(enemyFleet)
        target = None
        for i in self.planet.items():
            if type(i[0]) == tuple:
                continue
            if i[0] not in self.planetInDanger and i[0] != planetId:
                target = i[1].getInformation()[0]
                break
        if target:
            return self.getEscapeFleet(planet, target)
        else:
            return 0


    def getEscapeFleet(self, planet:Planet, destination) -> int:
        url = "game.php?page=my_fleet1"
        __args = {}

        target = {'galaxy': destination[0], 'system': destination[1], 'planet': destination[2], 'type': destination[3]}

        next(self.taskCore({"type":4,"func":planet.updateResources}))
        __args.update(dict(zip(['type', 'mission', 'speed'], [1, 4, 1])))
        __args.update(planet.getFleet())
        __args.update(target)

        res = self._post(url, __args)  # get fleet information
        if res['status'] != 0:
            return 0
        __args.update({'token': res['data']['result']['token']})

        if res['status'] == 0:
            if res['data']['status'] == 'error':
                return 0
            __args['token'] = res['data']['result']['token']
        space:int = res['data']['result']['fleetroom']
        cost:int = res['data']['result']['consumption']

        resource = planet.getResources()
        availSpace = space - cost
        if availSpace < 1 or space < 1:
            return 0
        deCost = min(availSpace, float(resource['deuterium']) - cost)
        __args.update({'deuterium': deCost})
        __args.update({'metal': min(float(resource['metal']), (availSpace - deCost) // 4 * 3)})
        __args.update({'crystal': min(float(resource['crystal']), (availSpace - deCost) // 4 * 1)})
        url = "game.php?page=fleet3"
        noShip = True

        for i in __args.keys():
            if i.startswith('ship'):
                noShip = False
                break
        self.logger.debug(f" {__args} {noShip}")
        if noShip:
            self.logger.info(f"{planet.getInformation()[0]} no ship available")
            return 0
        else:
            self.logger.debug(f"{planet.getInformation()[0]} ship available")   


        res = self._post(url, __args)  # send fleet
        if res['status'] == 0:
            self.logger.info( res['data'])
            return int(res['data']['result']['id'])
        else:
            return 0

    async def Detect(self):
        """
        check if there is enemy attacking us
        if there is, escape
        """
        while True:
            try:
                self.checkEnemy()
            except Exception as e:
                self.logger.error(e)
                import traceback
                traceback.print_exc()
            await asyncio.sleep(self.info['detectInterval'])

    async def addAttackTask(self):
        """Generates a new attack task"""
        task = {}
        targetIndex = 0
        while True:
            target = self.attackTargetList[targetIndex]
            targetIndex = (targetIndex + 1) % len(self.attackTargetList)

            task['target'] = target
            task['level'] = self.attackLevel
            task['type'] = 1
            task['times'] = self.attackTimes
            task['from'] = self.attackFrom
            self.logger.debug(task)
            try:
                sleepTime = next(self.taskCore(task))
            except Exception as e:
                self.logger.error(e)
                sleepTime = 30

            self.logger.info(f"{task['from']} attacking! waiting for {sleepTime} seconds")  # TODO: identify success or not
            await asyncio.sleep(sleepTime)

    async def addExploreTask(self):
        """Generates a new explore task"""
        task = {}
        while True:
            target = self.exploreTargetList[0]
            task['target'] = target
            task['level'] = self.exploreLevel
            task['type'] = 1
            task['times'] = self.exploreTimes
            task['from'] = self.exploreFrom
            try:
                sleepTime = next(self.taskCore(task))
            except Exception as e:
                self.logger.error(e)
                sleepTime = 30
            self.logger.info(f"{task['from']} exploring! waiting for {sleepTime} seconds")
            await asyncio.sleep(sleepTime)

    def asyncTaskGenerator(self):
        """
        Generates all async tasks here
        """
        taskLst = []
        if self.isAttack:
            attackTask = asyncio.create_task(self.addAttackTask())
            taskLst.append(attackTask)
        if self.isExplore:
            exploreTask = asyncio.create_task(self.addExploreTask())
            taskLst.append(exploreTask)
        if self.isEscaping:
            escapeTask = asyncio.create_task(self.Detect())
            taskLst.append(escapeTask)
        taskLst.append(asyncio.create_task(self.enableAutoLogin()))
        return taskLst

    async def gatherTask(self):
        taskLst = self.asyncTaskGenerator()
        await asyncio.gather(*taskLst)

    def runTask(self):
        self.startup()
        asyncio.run(self.gatherTask())

    # extra function area

    def showPlanetId(self):
        self.login()
        print("最后一位为0是行星，为1是月球")
        url = "game.php?page=buildings"
        result = self._post(url, {})
        if result['status'] != 0:
            self.logger.warning(f"Wrong planet id")
            return
        result = result['data']
        for i in result['result']['buildInfo']['result']['Planets'].items():
            data = i[1]
            self.planet[i[0]] = list(
                map(int,
                    [data['galaxy'], data['system'], data['planet'], data['planet_type'] == '3']))
            print(i[0], self.planet[i[0]])


    def migratePlanet(self, planetId, target):
        """
        migrate planet to target
        :param planetId: planet id
        :param target: target planet id
        :return:
        """
        # WARNING YOU SHOULD BE RESPONSIBLE FOR YOUR OWN ACTION
        # ANY ILLEGAL ACTION WILL BE YOUR RESPONSIBILITY
        url = "game.php?page=items&mod=2&type=100000"

        if len(target) != 3 or type(target) not in [list, tuple]:
            self.logger.warning(f"target should be a list of length 3, your input is {len(target)}")
            return

        __args = {'id': planetId}
        __args.update({'target_galaxy': target[0]})
        __args.update({'target_system': target[1]})
        __args.update({'target_planet': target[2]})
        result = self._post(url, __args)
        if result.get('status') == 0:
            if result['data']['status'] != 'ok':
                self.logger.error(f"{result['data']['error']}")
            else:
                data: dict = result['data']['result']
                self.logger.info(f"Migrate {data.get('planet_id')} to"
                             f" {data.get('galaxy')}.{data.get('system')}.{data.get('planet')} success")


if __name__ == "__main__":
    pass
