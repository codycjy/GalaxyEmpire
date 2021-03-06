import logging
import queue
import asyncio
from collections import defaultdict

logging.getLogger("requests").setLevel(logging.CRITICAL)

import requests

from src.Core.GalaxyCore import GalaxyCore
from src.Core.Planet import Planet

class Galaxy(GalaxyCore):
    def __init__(self, username: str, password: str, server: str):
        super().__init__(username, password, server)
        self.attackLevel=None
        self.fleetOnPlanet=defaultdict(dict)
        self.resourcesOnPlanet=defaultdict()
        self.attackedPlanet=defaultdict(int)
        self._planet={}
        # get all the planet and initalize them


    def getTasks(self,attackTargetList,attackLevel,exploreTargetList,exploreLevel,taskEnabled,fleetLevel):
        self.attackLevel=attackLevel[0]
        self.attackTargetList=attackTargetList
        self.attackTimes=attackLevel[1]


        self.exploreLevel=exploreLevel[0]
        self.exploreTargetList= exploreTargetList
        self.exploreTimes=exploreLevel[1]


        self.isAttack=taskEnabled['attack']
        self.isExplore=taskEnabled['explore']
        self.isEscaping=taskEnabled['escape']

        self.fleetLevel=fleetLevel


    def taskCore(self,task):
        """
        all task based on task Core func including relogin
        0:relogin 1:attack&&explore 2:escape 
        """

        if task['type'] == 0:
            self.relogin()
            yield 0
        elif task['type'] == 1:
            waittime=30
            for _ in range(task['times']):
                waittime=max(self.Attack(task['target'], task['level'])['waittime'],waittime)
            yield waittime
                
        elif task['type'] == 2:
            self.Escape(task['planetId'],task['enemyFleet'])
            yield 0  
        
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
            result= next(self.taskCore({'type':0}))

    def getAttackFleet(self,target,level):
        url="game.php?page=my_fleet1"
        __args={}
        __args.update(dict(zip(['type','mission'],[4,15] if 50<level<100 else [1,1])))
        if not self.fleetLevel[level]:
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
            
    def updateBuildingInfo(self):
        url="game.php?page=buildings"
        result=self._post(url)
        if result['status'] == 0:
            buildInfo=result['data']
            self.planet.clear()
            for i in buildInfo['result']['buildInfo']['result']['Planets'].items():
                planet=(i[1]['galaxy'],i[1]['system'],i[1]['planet'],i[1]['planet_type'])
                self.planetIdDict[i[0]]=planet
                self.planetIdDict[planet]=i[0]
                planetInformation=self.getSession()
                planetInformation.update({'server':self.server,'planetId':i[0],'position':planet})
                self.planet[i[0]]=Planet(planetInformation)
        else:
            return{'status':-1,'data':result['data']}


    def checkEnemy(self):
        """
        check whethe there is enemy attacking us
        """

        url="game.php?page=fleet&action=detected"
        result = self._post(url)
        logging.debug(result)
        if result['status'] != 0:
            return {'status':-1}
        result=result['data']['result'] # attacking enemies
        logging.info(result)
        self.attackedPlanet.clear()
        for i in result:
            plannetId = None
            target=(i['endGalaxy'],i['endSystem'],i['endPlanet'],i['endType'])
            plannetId=self.planetIdDict[target]
            if not plannetId:
                logging.warning("wrong planet id")
                continue
            logging.info("enemy attacking us"+str(plannetId))
            self.attackedPlanet[plannetId]=1
            result=next(self.taskCore({'type':2,'planetId':plannetId,'enemyFleet':i['fleet']}))


    def Escape(self,planetId:str,enemyFleet):
        """
        escape from planet
        """
        url='game.php?page=my_fleet1'
        __args={} 
        planet=self.planet[planetId]
        planet.updateResources()
        __args.update(planet.getFleet())
        __args.update({'mission':4})
        logging.info(enemyFleet)
        target=None
        for i in self.planet.items():
            if(type(i[0])==tuple):continue
            if i[0] not in self.attackedPlanet.keys() and i[0]!=planetId:
                target=i[1].getInformation()[0]
                break
        if target: 
            self.getEscapeFleet(planet,target)
        # self.changePlanet(planetId)

    def getEscapeFleet(self,planet,destination):
        url="game.php?page=my_fleet1"
        __args={}

        target={'galaxy':destination[0],'system':destination[1],'planet':destination[2],'type':destination[3]}

        __args.update(dict(zip(['type','mission','speed'],[1,4,1])))
        __args.update(planet.getFleet())
        __args.update(target)

        logging.debug(__args)
        res=self._post(url,__args) # get fleet information
        __args.update({'token':res['data']['result']['token']})

        if res['status']==0:
            if res['data']['status'] =='error':return 
            __args['token']=res['data']['result']['token']
        space=res['data']['result']['fleetroom']
        cost=res['data']['result']['consumption']

        resource = planet.getResources()
        availSpace = space - cost
        if availSpace < 1 or space<1 :
            return
        deCost=min(availSpace,resource['deuterium']-cost)
        __args.update({'deuterium':deCost})
        __args.update({'metal':min(resource['metal'],(availSpace-deCost)//4*3)})
        __args.update({'crystal':min(resource['crystal'],(availSpace-deCost)//4*1)})
        url="game.php?page=fleet3"
        res=self._post(url,__args) # send fleet
        logging.info(res['data'])

        logging.debug(__args)

    async def Detect(self):
        """
        check if there is enemy attacking us
        if there is, escape
        """
        while True :
            self.checkEnemy()
            await asyncio.sleep(60)

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
            task['times'] = 1 
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
            task['times'] = 1 
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
            escapeTask=asyncio.create_task(self.Detect())
            await escapeTask

    def run(self):
        asyncio.run(self.asyncTaskGenerator())



if __name__ == "__main__":
    print('start')
    g=Galaxy('','','')
    g.login()



