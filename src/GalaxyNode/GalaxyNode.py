import asyncio
from multiprocessing import Process
from multiprocessing.connection import Connection

from src.Core.Galaxy import Galaxy


class GalaxyNode(Galaxy, Process):
    def __init__(self, conn: Connection, logger=None):
        Galaxy.__init__(self)  # TEMP use
        Process.__init__(self)
        self.conn = conn
        self.logger = logger

    def ping(self):
        return "pong"

    def run(self):
        print("Starting galaxy node")
        asyncio.run(self.runThreadTask())

    async def pipeCommunicate(self):
        while True:
            if self.conn.poll():
                query = self.conn.recv()
                self.sendMsg(self.queryHandler(query))
            await asyncio.sleep(0.5)

        
    async def runThreadTask(self):
        taskList = self.asyncTaskGenerator()
        asyncTaskList=[]
        for task in taskList:
            asyncTaskList.append(asyncio.create_task(task))
        await asyncio.gather(asyncio.create_task(self.pipeCommunicate()), *asyncTaskList)

    def sendMsg(self, msg):
        self.conn.send(msg)

    def queryHandler(self, query):  # TODO:
        if query == "ping":
            response = self.ping()
            return response

        return "Unknown query"

    def testLogin(self):
        print(f"Testing login for {self.server}@{self.username}")
        loginResult = self.login()
        if loginResult['status'] == 0:
            return {'status': True, 'msg': 'Login successfully'}
        else:
            return {'status': False, 'msg': loginResult['err_msg']}
