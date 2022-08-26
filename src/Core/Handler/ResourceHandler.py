from . import ENABLE_MYSQL
import logging


class ResourceHandler:
    """
    Recording all the resources and save them to database
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




    # receive fleet and planet information
