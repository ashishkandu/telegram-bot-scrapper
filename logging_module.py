import os
import logging
from variables import log_file_name


curr_path = os.path.dirname(os.path.realpath(__file__))
LOG_FILENAME = os.path.join(curr_path, log_file_name)

# Logging code
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_formatter = logging.Formatter('[%(levelname)s]: %(name)s %(asctime)s - %(message)s')

# logs to the console only with the help of StreamHandler()
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
file_handler = logging.FileHandler(LOG_FILENAME)
file_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.info("Starting up bot\n")

