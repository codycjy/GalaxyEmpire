import cmd
import os.path
import sys

from src.GalaxyNode.GalaxyController import GalaxyController


class GalaxyCmd(cmd.Cmd):
    """Simple command processor example."""
    prompt = '> '
    intro = "Welcome to Galaxy CMD! Type ? to list commands"

    def __init__(self, **kwargs):
        super().__init__()
        self.gc = GalaxyController()
        self.cfgPath = kwargs.get('path', 'NodeConfigs')
        self.logger = kwargs.get('logger', None)

        if not os.path.exists(self.cfgPath):
            os.mkdir(self.cfgPath)
            print('Config directory not found, created')
            sys.exit()
        self.needTestLogin = kwargs.get('enable_test_login', True)

    def do_init(self, line=None):
        print("Controller initialized")
        self.gc = GalaxyController()

    def help_init(self):
        print("Clear all nodes and initialize controller")

    def do_add(self, line):  # not done yet
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

    def do_show(self):
        result = self.gc.getAllNodesInfo()
        for i in result:
            print(i)

    def help_show(self):
        print("Show all nodes")

    def do_exit(self, line):
        sys.exit()

    def manualAddTask(self):
        pass  # TODO complete it later low priority


if __name__ == '__main__':
    GalaxyCmd().cmdloop()
