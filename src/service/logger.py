from loguru import logger
import sys


def init_logger():
    format_info = "<red>GRID_BOT</red>: <green>{time:HH:mm:ss}</green> | <blue>{level}</blue> | <level>{message}</level>"
    logger.remove()
    logger.add(sys.stdout, colorize=True, format=format_info, level="INFO")
    return logger
    
init_logger()
