import logging
import datetime
import os

requestLogger=logging.getLogger('requests')

class GalaxyLogger(logging.Logger):
    def __init__(self, path, level=logging.INFO, name='Logger'):

        if not os.path.exists(path):
            os.makedirs(path)

        super().__init__(name, level)
        formatter = logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - '
                                      '%(name)s %(levelname)s: %(message)s')
        
        
        fileHandler=logging.FileHandler(
            f"{path}/{name if name!='logger'else ''} "
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.log")
        fileHandler.setFormatter(formatter)
        fileHandler.setLevel(level)
        self.addHandler(fileHandler)

        consoleHandler=logging.StreamHandler()
        consoleHandler.setFormatter(formatter)
        consoleHandler.setLevel(min(level,logging.DEBUG))
        self.addHandler(consoleHandler)

        self.propagate = True





if __name__ == '__main__':
    pass


