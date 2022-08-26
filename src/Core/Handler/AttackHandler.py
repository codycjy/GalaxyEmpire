from . import ENABLE_MYSQL
import logging


class AttackHandler:
    """
    Recording attack information and save them to database
    """
    def __init__(self):
        if not ENABLE_MYSQL:
            logging.info("MYSQL is not enabled")
        pass

    def logToDb(self):
        if ENABLE_MYSQL:
            self.__logToDb()
        else:
            pass

    def __logToDb(self):
        pass


if __name__ == '__main__':
    A = AttackHandler()
