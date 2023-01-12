import cmd
import json
import os.path
import sys
from json import JSONDecodeError

from src.Core.GalaxyCore import GalaxyCore
from src.GalaxyNode.GalaxyController import GalaxyController


class GalaxyCmd(cmd.Cmd):
    """Simple command processor example."""
    prompt = '> '
    intro = "Welcome to Galaxy CMD! Type ? to list commands"

    def __init__(self, path, **kwargs):
        super().__init__()
        self.gc = GalaxyController(
            loggingLevel=kwargs.get("loggingLevel"),
            loggingPath=kwargs.get("loggingPath")
        )
        self.cfgPath = path
        self.logger = kwargs.get('logger', None)

        if not os.path.exists(self.cfgPath):
            os.mkdir(self.cfgPath)
            print('Config directory not found, created')
            # TODO create fleet json
            with open(f"{self.cfgPath}/fleet.json", 'w') as f:
                f.write(json.dumps(GalaxyCore.fleet, indent=4))
            sys.exit()

        if not os.path.exists(self.cfgPath+'/fleet.json'):
            print('Fleet config not found, created')
            with open(f"{self.cfgPath}/fleet.json", 'w') as f:
                try:
                    f.write(json.dumps(GalaxyCore.fleet, indent=4))
                except JSONDecodeError:
                    print('Error! Invalid fleet config')
                    sys.exit()
                except Exception as e:
                    print(e)
                    sys.exit()
        else:
            with open(f"{self.cfgPath}/fleet.json", 'r') as f:
                fleet = json.load(f)
            self.gc.defaultFleet = fleet

        self.needTestLogin = kwargs.get('enable_test_login', True)
        # TODO add logging path

    def do_init(self, line=None):
        print("Controller initialized")
        self.gc = GalaxyController()

    def help_init(self):
        print("Clear all nodes and initialize controller")

    def do_add(self, line):  # not done yet
        """
        Uselss func
        may remove next time
        """
        username = input("username:")
        password = input("password:")
        server = input("server:")
        self.manualAddTask()

    def do_autoadd(self, line):
        self.gc.autoGetNode(self.cfgPath)

    def do_start(self, line):
        self.gc.start()

    def help_start(self):
        print("Start all nodes")

    def help_autoadd(self):
        print("Load configs from NodeConfigs and add nodes if login successfully")

    def help_add(self):
        print("Not done yet, not prepare to use")
        print("Add a node, and test login ")

    def do_show(self, line):
        result = self.gc.getAllNodesInfo()
        for i in result:
            print(i)

    def help_show(self):
        print("Show all nodes")

    def do_exit(self, line):
        sys.exit()

    def manualAddTask(self):
        pass  # TODO complete it later low priority

    def cmdloop(self, **kwargs):
        while True:
            try:
                super().cmdloop("")
            except Exception as e:
                print("recovered from exception {}".format(e))


if __name__ == '__main__':
    GalaxyCmd().cmdloop()
