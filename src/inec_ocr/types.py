#!/usr/bin/env python

"""types.py: Contains type aliases used in this project"""

__author__ = "Similoluwa Okunowo"
__email__ = "rexsimiloluwa@gmail.com"

from typing import (
    Tuple,
    List,
    NamedTuple,
    Union,
    Dict,
)

class BoundingBox(NamedTuple):
    x1: int
    y1: int
    x2: int
    y2: int

class ColumnData(NamedTuple):
    text: str
    bbox: BoundingBox

OCRBBoxesResultType = List[List[List[float]]]
OCRTextsResultType = List[str]
OCRScoresResultType = List[float]

class OCRResultType(NamedTuple):
    bboxes: OCRBBoxesResultType
    texts: OCRTextsResultType
    scores: OCRScoresResultType

class ColumnTuple(NamedTuple):
    column_data: List[ColumnData]
    column_idx: int

Column = List[ColumnData]
AllColumns = List[List[ColumnData]]
ResultsMap = Dict[str, Union[int, str, float,  None]]
