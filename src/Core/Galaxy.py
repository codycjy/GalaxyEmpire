import logging
import queue
import asyncio

import requests

from src.Core.GalaxyCore import GalaxyCore

class Galaxy(GalaxyCore):
    def __init__(self, username: str, password: str, server: str):
        super().__init__(username, password, server)
        self.attackTargetList=[{'planet':6,'system':47,'galaxy':137}]

        self.attackLevel=None


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
            finally:
                pass #TODO
            pass
        else:
            raise Exception('Error while getAttackFleet')
        return __args

    def Attack(self,target,level):
        url='game.php?page=fleet3'
        additional_args={'staytime':1}

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
        attackTask=asyncio.create_task(self.addAttackTask())

        print(2333,'\n\n\n')
        if self.isAttack:
            await attackTask

    def run(self):
        asyncio.run(self.asyncTaskGenerator())

    def showPlanetId(self):
        for i in self.planet.items():
            print(i[0],end=' ')
        pass        

    async def addEscapeTask(self):
        """Generates a new escape task"""
        pass


    async def checkEnemy(self):
        """
        check whethe there is enemy attacking us
        """

    async def Escape(self,planetId):
        """
        escape from planet
        """
        pass



if __name__ == "__main__":
    print('start')
    g=Galaxy('','','')
    g.login()



