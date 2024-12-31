import logging
import colorlog
import json

config = json.load(open(".config.json"))

class LoggerManager:
    def __init__(self):
        logger = logging.getLogger(__name__)
        logging_level = logging.DEBUG if config["debugMode"] else logging.INFO
        logger.setLevel(logging_level)
        
        # Use colorlog's formatter
        formatter = colorlog.ColoredFormatter(
            "%(fg_bold_black)s%(asctime)s %(levelname_log_color)s%(levelname)-8.5s%(reset)s %(purple)s%(funcName)s %(reset)s%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            secondary_log_colors={
                'levelname': {
                    'ERROR': 'red',
                    'INFO': 'blue',
                    'DEBUG': 'green',
                    'WARNING': 'yellow'
                }
            }
        )
        
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(formatter)
        consoleHandler.setLevel(logging_level)

        logger.addHandler(consoleHandler)

        self.logger = logger