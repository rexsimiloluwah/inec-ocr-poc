#!/usr/bin/env python

"""logger.py: Custom logger"""

__author__ = "Similoluwa Okunowo"
__email__ = "rexsimiloluwa@gmail.com"
__credits__ = ["ChatGPT"]


import logging

# Create a logger
logger = logging.getLogger("my_logger")

# Set the logging level
logger.setLevel(logging.DEBUG)

# Create a file handler
file_handler = logging.FileHandler("logs.log")

# Set the logging level for the file handler
file_handler.setLevel(logging.INFO)

# Create a formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Add the formatter to the file handler
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)
