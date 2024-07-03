import logging

# Define ANSI color codes
COLOR_CODES = {
    'DEBUG': '\033[94m',   # Blue
    'INFO': '\033[92m',    # Green
    'WARNING': '\033[93m', # Yellow
    'ERROR': '\033[91m',   # Red
    'CRITICAL': '\033[95m' # Magenta
}

RESET_CODE = '\033[0m'    # Reset color

class ColorFormatter(logging.Formatter):
    def format(self, record):
        log_color = COLOR_CODES.get(record.levelname, RESET_CODE)
        message = super().format(record)
        return f"{log_color}{message}{RESET_CODE}"

# Set up the logger
def setup():
    log = logging.getLogger('werkzeug')
    log.disabled = True

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # formatter = ColorFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = ColorFormatter('%(asctime)s - %(levelname)s - %(message)s')
    formatter.datefmt = '%Y-%m-%d %H:%M'
    console_handler.setFormatter(formatter)


    logger.addHandler(console_handler)

    return logger