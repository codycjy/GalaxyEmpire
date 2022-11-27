import logging
import time
from multiprocessing import Process, Pipe

from src.Core.Galaxy import Galaxy


class GalaxyNode(Galaxy, Process):
    def __init__(self, conn: Pipe, logger=None):
        Galaxy.__init__(self)  # TEMP use
        Process.__init__(self)
        self.conn = conn
        self.logger = logger

    def ping(self):
        return {'status': True, 'msg': 'pong'}

    def start(self):
        logging.info("Node started")
        self.runTask()
        while True:
            if self.conn.poll():
                query = self.conn.recv()
                self.queryHandler(query)

    def sendMsg(self, msg):
        self.conn.send(msg)

    def queryHandler(self, query):
        if query == "ping":
            return self.ping()
        print(query)

    def testLogin(self):
        print("Testing login")
        loginResult = self.login()
        if loginResult['status'] == 0:
            return {'status': True, 'msg': 'Login successfully'}
        else:

            return {'status': False, 'msg': loginResult['err_msg']}
