#!/usr/bin/env python

"""ocr.py: Contains utility functions for the Optical Character Recognition (OCR) pipeline"""

__author__ = "Similoluwa Okunowo"
__email__ = "rexsimiloluwa@gmail.com"

import os
import pathlib
from typing import Tuple, List, Optional

import cv2
import numpy as np
from paddleocr import PaddleOCR

from .types import (
    OCRBBoxesResultType,
    OCRResultType,
    OCRScoresResultType,
    OCRTextsResultType,
)

# Instantiate the OCR engine
ocr = PaddleOCR(
    use_angle_cls=True,
    lang="en",
    det_model_dir="./models/det/en/en_PP-OCRv3_det_infer",
    rec_model_dir="./models/rec/en/en_PP-OCRv3_rec_infer",
    cls_model_dir="./models/cls/ch_ppocr_mobile_v2.0_cls_infer",
    cpu_threads=10,
    show_log=True,
)


def get_ocr_engine():
    return ocr


def extract_text(img_path: str) -> OCRResultType:
    """Returns the extracted texts and their associated bounding boxes and confidence scores.

    Args:
        img_path (str): The path to the image file

    Returns:
        tuple: A tuple containing
        - bboxes (list): List of the bounding boxes associated with the extracted texts
        - texts (list): List of the extracted texts
        - scores (list): List of the confidence scores associated with the extracted texts
    """
    result = ocr.ocr(img_path, cls=True)

    # Obtain the bboxes, texts, and scores
    result = result[0]
    bboxes = [line[0] for line in result]
    texts = [line[1][0] for line in result]
    scores = [line[1][1] for line in result]

    # Return the results
    return bboxes, texts, scores


def filter_text_predictions(
    bboxes: OCRBBoxesResultType,
    texts: OCRTextsResultType,
    scores: OCRScoresResultType,
    conf_thresh: Optional[float] = 0.6,
) -> Tuple[OCRBBoxesResultType, OCRTextsResultType]:
    """Filters the extracted texts based on their associated confidence scores.

    Args:
        bboxes (OCRBBoxesResultType): List of the bounding boxes associated with the extracted texts
        texts (OCRTextsResultType): List of the extracted texts
        scores (OCRScoresResultType): List of the confidence scores associated with the extracted texts
        conf_thresh (Optional[float]): A threshold value specifying the minimum confidence score allowed

    Returns:
        tuple: A tuple containing
        - filtered_bboxes: List of the filtered bounding boxes
        - filtered_texts: List of the filtered texts
    """
    filtered_bboxes = []
    filtered_texts = []

    for i in range(0, len(bboxes)):
        text = texts[i]
        conf = scores[i]

        # filter out text localizations with weak confidence scores
        if conf > conf_thresh:
            # compute the bounding box coordinates
            bbox = np.array(bboxes[i]).astype(np.int32)
            x1 = min(bbox[:, 0])
            y1 = min(bbox[:, 1])
            x2 = max(bbox[:, 0])
            y2 = max(bbox[:, 1])

            # update the filtered bounding boxes and extracted texts accordingly
            filtered_bboxes.append((x1, y1, x2, y2))
            filtered_texts.append(text)

    # Return the filtered bboxes and texts
    return filtered_bboxes, filtered_texts


def draw_ocr(img: np.ndarray, bboxes: OCRBBoxesResultType):
    """Draw the bounding boxes of the extracted texts on the OCR'd image.

    Args:
        img (np.ndarray): The input (OCR'd) image
        bboxes (OCRBBoxesResultType): List of the bounding boxes associated with the extracted texts

    Returns:
        np.ndarray: The annotated image after drawing the bounding boxes
    """
    img_copy = img.copy()

    # Generate a random color for the bounding rects
    # TODO: ensure that the color is of a dark shade
    # random_color = tuple([np.random.randint(0, 255) for _ in range(3)])
    color = (0, 0, 255)

    # Loop through all the bouding boxes
    for bbox in bboxes:
        bbox = np.array(bbox).astype(np.int32)
        xmin = min(bbox[:, 0])
        ymin = min(bbox[:, 1])
        xmax = max(bbox[:, 0])
        ymax = max(bbox[:, 1])

        # Draw the bounding box rect on the image
        cv2.rectangle(img_copy, (xmin, ymin), (xmax, ymax), color, 2)

    # Return the annotated image
    return img_copy
