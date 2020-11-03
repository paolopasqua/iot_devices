

import logging

class LoggerUtility(object):
    """
    docstring
    """
    
    def get_logger(namefile="log.log", level=logging.DEBUG):
        logger = logging.getLogger(__name__)
        logger.setLevel(level)
        ch = logging.FileHandler(namefile)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger