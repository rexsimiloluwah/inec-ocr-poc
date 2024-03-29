#!/usr/bin/env python

"""common.py: Contains common utility functions"""

import re
from difflib import SequenceMatcher
from typing import Any, Optional

import cv2
import numpy as np


def is_near(a: int, b: int, min_dist: Optional[int] = 5) -> bool:
    """Checks if two points are near each other.

    Args:
        a (int): First point
        b (int): Second point
        min_dist (Optional[int]): Minimum acceptable distance between the two points

    Returns:
        bool: A boolean indicating whether the points are near each other
    """
    return abs(a - b) <= min_dist


def similar(a: str, b: str) -> float:
    """Computes the similarity index between two words.

    Args:
        a (str): First word
        b (str): Second word

    Returns:
        float: A similarity index between the two words expressed as a percentage
    """
    return SequenceMatcher(None, a, b).ratio()


def is_number(variable: Any) -> bool:
    """Checks if a variable is a valid number using regex.

    Args:
        variable (Any): The test variable

    Returns:
        bool: A boolean indicating if the variable is a number or not
    """
    pattern = r"^[+-]?\d+(\.\d+)?$"  # regex pattern for number
    return bool(re.match(pattern, str(variable)))


def show_image(img: np.ndarray, name: Optional[str] = "image") -> None:
    """A utility function for displaying an image in the specified window using OpenCV.

    Args:
        img (np.ndarray): The input image
        name (Optional[str]): The name of the window
    """
    img_copy = img.copy()
    resized_img = cv2.resize(img_copy, (500, 500), cv2.INTER_AREA)
    cv2.imshow(name, resized_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
