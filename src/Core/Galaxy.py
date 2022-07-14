import logging
import queue
import asyncio
from collections import defaultdict

import requests

from src.Core.GalaxyCore import GalaxyCore

class Galaxy(GalaxyCore):
    def __init__(self, username: str, password: str, server: str):
        super().__init__(username, password, server)
        # self.attackTargetList=[{'planet':6,'system':47,'galaxy':137}]
        self.attackLevel=None
        self.fleetOnPlanet=defaultdict(dict)
        self.resourcesOnPlanet=defaultdict()


    def getTasks(self,attackTargetList,attackLevel,exploreTargetList,exploreLevel,taskEnabled):
        self.attackLevel=attackLevel[0]
        self.attackTargetList=attackTargetList
        self.attackTimes=attackLevel[1]


        self.exploreLevel=exploreLevel[0]
        self.exploreTargetList=exploreTargetList
        self.exploreTimes=exploreLevel[1]



        self.isAttack=taskEnabled['attack']
        self.isExplore=taskEnabled['explore']
        self.isEscaping=taskEnabled['escape']

    def taskCore(self,task):
        """
        all task based on task Core func including relogin
        0:relogin 1:attack&&explore 2:escape 
        """

        if task['type'] == 0:
            self.login()
        elif task['type'] == 1:
            waittime=30
            for _ in range(task['times']):
                waittime=max(self.Attack(task['target'], task['level'])['waittime'],waittime)
            yield waittime
                
        elif task['type'] == 2:
            yield 0  #TODO escape
            pass
        
    def getAttackFleet(self,target,level):
        url="game.php?page=my_fleet1"
        __args={}
        __args.update(dict(zip(['type','mission'],[4,15] if 50<level<100 else [1,1])))
        if not self.fleet[level]:
            logging.warning("wrong task")
            return
        else:
            __args.update(self.generateFleet(level))
            __args.update(target)

        logging.debug(__args)
        result=self._post (url,__args)
        if result['status']==0:
            try:
                __args.update({'token':result['data']['result']['token']})
            except KeyError:
                pass
        else:
            raise Exception('Error while getAttackFleet')
        return __args

    def Attack(self,target,level):
        url='game.php?page=fleet3'
        additional_args={'staytime':1}

        __args={}
        try:
            __args=self.getAttackFleet(target,level)
        except Exception:
            return {'status':-1,'waittime':0}

        logging.info('Attack')
        isFailed=True
        waittime=0
        if level>50:__args.update(additional_args)
        result=self._post(url,__args)
        if result['status']==0:
            if result['data']['status']=='ok':
                waittime=(float(result['data']['result']['backtime']))+30 # TODO consider whether use int later
                isFailed = False

        logging.info(isFailed)
        return {'status':-1,'waittime':waittime if not isFailed else 0} 
            
    async def addAttackTask(self):
        """Generates a new attack task"""
        task={}
        targetIndex=0
        while True:
            target=self.attackTargetList[targetIndex]
            targetIndex= (targetIndex+1)% len(self.attackTargetList)
            
            task['target']=target
            task['level'] = self.attackLevel
            task['type'] = 1
            task['times'] = 1 # TODO  make times and level together
            logging.debug(task)
            sleepTime=next(self.taskCore(task))
            logging.info(f"attacking! waiting for {sleepTime} seconds")
            await asyncio.sleep(sleepTime)

    async def addExploreTask(self):
        """Generates a new explore task"""
        task={}
        while True:
            target=self.attackTargetList[0]
            task['target']=target
            task['level'] = self.exploreLevel
            task['type'] = 1
            task['times'] = 1 # TODO  make times and level together
            sleepTime=next(self.taskCore(task))
            logging.info(f"Exploring! waiting for {sleepTime} seconds")
            await asyncio.sleep(sleepTime)
         
    async def asyncTaskGenerator(self):
        if self.isAttack:
            attackTask=asyncio.create_task(self.addAttackTask())
            await attackTask
        if self.isExplore:
            exploreTask=asyncio.create_task(self.addExploreTask())
            await exploreTask
        if self.isEscaping:
            escapeTask=asyncio.create_task(self.addEscapeTask())
            await escapeTask

    def run(self):
        asyncio.run(self.asyncTaskGenerator())

    def showPlanetId(self):
        self.updateBuildingInfo()
        for i in self.planet.items():
            print(i[0],end=' ')

    async def addEscapeTask(self):
        """Generates a new escape task"""
        self.checkEnemy()
        self.showPlanetId()
        pass


    def updateResources(self,planetId):
        """
        update resources of planet
        """
        res=self.changePlanet(planetId)
        for i in (res['result']['fleetInfo']['FleetsOnPlanet']):
            if i['id']==503:
                continue
            self.fleetOnPlanet[planetId]['id']=i['id']
            self.fleetOnPlanet[planetId]['count']=i['count']
        logging.info(self.fleetOnPlanet)
        pass


    def checkEnemy(self):
        """
        check whethe there is enemy attacking us
        """

        url="game.php?page=fleet&action=detected"
        result = self._post(url)
        logging.debug(result)
        if result['status'] != 0:
            return {'status':-1}
        result=result['data']['result']
        logging.info(result)

    



    async def Escape(self,planetId):
        """
        escape from planet
        """
        self.changePlanet(planetId)
        pass



if __name__ == "__main__":
    print('start')
    g=Galaxy('','','')
    g.login()



