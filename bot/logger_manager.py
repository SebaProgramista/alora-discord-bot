import logging
import json

config = json.load(open(".config.json"))

class LoggerManager:
    def __init__(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG if config["debugMode"] else logging.INFO)
        
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] %(message)s"))
        consoleHandler.setLevel(logging.DEBUG if config["debugMode"] else logging.INFO)

        logger.addHandler(consoleHandler)

        self.logger = logger