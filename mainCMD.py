from src.GalaxyNode.GalaxyCmd import GalaxyCmd

path = 'NodeConfigs'
if __name__ == '__main__':
    GalaxyCmd(path=path,enable_test_login=True).cmdloop()
