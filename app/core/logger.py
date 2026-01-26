

import logging

def setup_logger():

    logger_level = logging.INFO
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logger_level)

    logging.basicConfig(
        level=logger_level,
        handlers=[console_handler]
    )

    return None