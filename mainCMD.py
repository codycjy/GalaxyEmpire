import logging

from src.GalaxyNode.GalaxyCmd import GalaxyCmd

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    )


path = 'NodeConfigs'


if __name__ == '__main__':
    GalaxyCmd(path, enable_test_login=True,
              loggingLevel=logging.INFO, loggingPath='./logs').cmdloop()
