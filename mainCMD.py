import logging


from src.GalaxyNode.GalaxyCmd import GalaxyCmd
import multiprocessing_logging

# multiprocessing_logging.install_mp_handler()

path = 'NodeConfigs'
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    )
if __name__ == '__main__':
    GalaxyCmd(path=path,enable_test_login=True).cmdloop()
