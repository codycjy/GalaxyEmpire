import configparser
import os
from collections import defaultdict
from multiprocessing import Pipe

import multiprocessing_logging

from src.GalaxyNode.GalaxyNode import GalaxyNode

multiprocessing_logging.install_mp_handler()


class GalaxyController:
    def __init__(self):
        self.nodes = defaultdict(dict)
        self.conns = defaultdict(dict)
        self.cfgBackup = defaultdict(dict)

    def addNode(self, info, needLoginTest=True):
        conn1, conn2 = Pipe()
        node = GalaxyNode(conn2)
        node.getTaskNew(info)
        testLoginResult = node.testLogin()
        server = info['meta']['server']
        self.cfgBackup[server][info['meta']['username']] = info

        if needLoginTest:
            if testLoginResult['status']:
                self.nodes[server][info['meta']['username']] = node
                self.conns[server][info['meta']['username']] = conn1
                print(f"Node {info['meta']['username']} on {server} added")
                return {'status': True, 'msg': 'Node added successfully'}
            else:
                print(f"Node {info['meta']['username']} on {server} login failed: {testLoginResult['msg']}")
                return {'status': False, 'msg': testLoginResult['msg']}
        else:
            print(f"Node {info['meta']['username']} on {server} added")
            return {'status': True, 'msg': 'Node added successfully'}

    def getAllNodesInfo(self) -> list:
        nodes = []
        for i in self.nodes:
            for j in self.nodes[i]:
                nodes.append(f"Server: {i}, Username: {j}")
        return nodes

    def checkAlive(self):  # Alpha version
        for server in self.nodes.values():
            for nodes in server.keys():
                if not nodes.is_alive():
                    try:
                        print(f"Node {nodes} on {server} is dead, restarting")
                        self.addNode(self.cfgBackup[server][nodes], False)
                        self.nodes[server][nodes].start()
                        print(f"Node {nodes} on {server} restarted")
                    except Exception as e:
                        print(e)

    def loadConfigs(self, path: str = 'NodeConfigs'):
        configs = []
        curPath = os.getcwd()  # TODO check directory
        if not os.path.exists(curPath + '/' + path):
            print('Error! Config directory not found')
            os.mkdir(curPath + '/' + path)
            return None
        cfgPath = curPath + f'/{path}'
        configPath = [i for i in os.listdir(cfgPath) if i.endswith('.ini')]
        if not configPath:
            print("Warning! No config file found")
        config = configparser.ConfigParser()
        for i in configPath:
            try:
                config.read(cfgPath + f'/{i}')
                configs.append(self.parseConfig(config))
            except Exception as e:
                print(e)
        return configs

    def findNode(self, username, server):
        return self.nodes.get(server).get(username, None)

    def start(self):
        for i in self.nodes:
            for j in self.nodes[i]:
                print(f"Starting node {j} on {i}")
                self.nodes[i][j].start()
        print("All nodes started")

    def stop(self):
        for i in self.nodes:
            for j in self.nodes[i]:
                self.nodes[i][j].terminate()

    def sendMsg(self, username, server, msg):
        self.conns[username][server].send(msg)

    def recvMsg(self, username, server):  # TODO Change it later
        return self.conns[username][server].recv()

    def autoGetNode(self, path):
        nodeList = self.loadConfigs(path)
        if nodeList:
            for i in self.loadConfigs(path):
                self.addNode(i)

    def parseConfig(self, config):  # TODO rewrite task with dict
        nodeConfig = defaultdict(dict)
        isError = False
        if config.has_section('Task') and config.has_section('Base'):
            tasks = config.items('Task')
            infoRaw = config.items('Base')
            infoDict = {}
            for i in infoRaw:
                infoDict[i[0]] = i[1]
            if not infoDict.get('username', None) \
                    or not infoDict.get('password', None) \
                    or not infoDict.get('server', None):
                isError = True
                print("Error: Base info is not complete")
            else:
                nodeConfig['meta'] = infoDict

            for i in tasks:
                try:
                    if i[0] == 'attack' and int(i[1]) == 1:
                        nodeConfig['enabled']['attack'] = True
                        attackConfig = self.parseTask(config.items('Attack'))
                        if attackConfig:
                            nodeConfig['attack'] = attackConfig
                        else:
                            print("Error in attack config")
                            isError = True
                    if i[0] == 'explore' and int(i[1]) == 1:
                        nodeConfig['enabled']['explore'] = True
                        exploreConfig = self.parseTask(config.items('Explore'))
                        if exploreConfig:
                            nodeConfig['explore'] = exploreConfig
                        else:
                            print("Error in explore config")
                            isError = True
                    if i[0] == 'escape' and int(i[1]) == 1:
                        nodeConfig['enabled']['escape'] = True
                except ValueError:
                    print("Error in config file")
                    return None
        else:
            print('Error! Config file is not valid, Required sections: Task, Base')
        if isError:
            return None
        return nodeConfig

    def parseTask(self, rawTask):
        data = {}
        task = {}
        isError = False
        for i in rawTask:
            data[i[0]] = i[1]
        try:
            target = data['target'].split(',')
            task['target'] = [list(map(int, i.split('.'))) for i in target]
        except ValueError:
            isError = True
            # TODO low priority add to loggers
        except Exception as e:
            print(e)

        try:
            times = int(data['times'])
            task['times'] = times
        except ValueError:
            isError = True
            print(2333)  # TODO finish it later

        try:
            startFrom = int(data['start_from'])
            task['startFrom'] = startFrom
        except ValueError:
            isError = True
            print(2333)  # TODO finish it later

        try:
            level = int(data['fleet'])
            task['level'] = level
        except ValueError:
            isError = True
            print(2333)

        if isError:
            return None
        return task

    def autoLoadTask(self, path):
        for i in self.loadConfigs(path):
            self.addNode(i)

    # following are test func

    def test(self):
        # let configparse parse the config file
        for i in self.loadConfigs():
            self.addNode(i)
        # config = configparser.ConfigParser()
        # config.read('./NodeConfigs/config1.ini')
        # self.parseConfig(config)


if __name__ == '__main__':
    pass
