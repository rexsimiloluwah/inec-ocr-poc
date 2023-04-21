#!/usr/bin/env python

"""document.py: Contains utility functions for parsing the INEC form document OCR results"""

__author__ = "Similoluwa Okunowo"
__email__ = "rexsimiloluwa@gmail.com"
__credits__ = ["Adrian Rosebrock (for the four point transform algorithm)"]

from typing import (
    List,
    Union,
    Tuple,
    Optional,
    Dict
)

import cv2
import numpy as np
from scipy.spatial import distance as dist

from .common import similar, is_near, is_number
from .types import (
    ColumnData,
    ColumnTuple,
    AllColumns,
    ResultsMap
)
from .constants import (
    POLITICAL_PARTIES,
    POLLING_UNIT_DATA_FIELDS,
    ELECTION_TYPES,
    POLLING_UNIT_REGISTRATION_INFO_FIELDS,
)


def get_political_parties_column(
    all_cols: AllColumns, thresh: Optional[int] = 10
) -> Union[ColumnTuple, None]:
    """Returns the column that contains the political parties names.

    Args:
        all_cols (AllColumns): All the columns extracted from the OCR'd image
        thresh (Optional[int]): A heuristic value denoting a minimum number of political parties that must be in the column

    Returns:
        tuple: A tuple containing
        - col (ColumnData): Column data
        - col_idx (int): Index of the column in list of all the extracted columns
    """
    political_parties_set = set(POLITICAL_PARTIES)

    # Loop through all the columns
    for col_idx, col in enumerate(all_cols):
        if not col:
            continue
        col_values = [cell[0] for cell in col]
        col_set = set(col_values)
        # Compute the intersection of the political parties set and column set
        intersection = col_set & political_parties_set

        # Check the number of elements in the intersection set
        count = len(list(intersection))

        # Return the column data and its column index if the column contains a minimum number of political parties as values.
        # This minimum number is specified by the 'thresh' parameter
        if count > thresh:
            return (list(filter(lambda x: x[0] in POLITICAL_PARTIES, col)), col_idx)

    return None


def get_polling_unit_data_fields_column(
    all_cols: AllColumns,
    values_thresh: Optional[int] = 2,
    similarity_thresh: Optional[int] = 0.8,
) -> Union[ColumnTuple, None]:
    """Returns the column that contains the polling unit (PU) data fields.

    Args:
        all_cols (AllColumns): All the columns extracted from the OCR'd image
        values_thresh (Optional[int]): A heuristic value denoting the minimum number of PU data fields in the column
        similarity_thresh (Optional[int]): A heuristic value denoting the threshold for the similarity index between the OCR'd and the actual field name

    Returns:
        tuple: A tuple containing
        - col_data (ColumnData): Column data
        - col_idx (int): Index of the column in list of all the extracted columns
    """
    # Loop through all the columns
    for col_idx, col in enumerate(all_cols):
        if not col:
            continue
        count = 0
        out = []

        # List of the texts in the current column
        col_values = [cell[0] for cell in col]

        # Loop through all the polling unit data fields
        for field in POLLING_UNIT_DATA_FIELDS:
            # Loop through all the texts for this column
            for value_idx, value in enumerate(col_values):
                # Check if the cell value is similar to any of the polling unit data fields
                if similar(field, value) > similarity_thresh:
                    count += 1
                    out.append((field, col[value_idx][1]))
                    continue

        # Check if the number of values in the column is greater than the specified threshold
        if count > values_thresh:
            return (out, col_idx)

    return None


def get_political_parties_results_column(
    all_cols: AllColumns,
    pol_parties_column: ColumnTuple,
    thresh: Optional[int] = 3,
) -> Union[ColumnTuple, None]:
    """Returns the column containing the political parties vote results.

    Args:
        all_cols (AllColumns): All the columns extracted from the OCR'd image
        pol_parties_column (ColumnTuple): Tuple containing the political parties and its column index
        thresh (Optional[int]): A heuristic value denoting the minimum number of OCR'd texts that must be in the column

    Returns:
        tuple: A tuple containing
        - col (ColumnData): Column data
        - col_idx (int): Index of the column in the list of all the extracted columns
    """
    if not pol_parties_column:
        return None

    pol_parties_column_data, pol_parties_column_idx = (
        pol_parties_column[0],
        pol_parties_column[1],
    )
    pp_bboxes = [cell[1] for cell in pol_parties_column_data]

    for col_idx, col in enumerate(all_cols):
        if col_idx != pol_parties_column_idx:
            col_bboxes = [cell[1] for cell in col]

            # The starting y-coordinates for the bboxes must be close,
            # and the ending-x coordinate of the political party name bbox must be
            # quite close to the starting x-coordinate of the result figures column bbox we are looking for
            k = map(
                lambda bbox: any(
                    [
                        (
                            is_near(bbox[1], pp_bbox[1], 10)
                            and is_near(bbox[0], pp_bbox[2], 60)
                            and pp_bbox[2] < bbox[0]
                        )
                        for pp_bbox in pp_bboxes
                    ]
                ),
                col_bboxes,
            )

            # Check if the column contains a minimum number of results for the political parties.
            # This minimum number is determined by the 'thresh' parameter
            if sum(list(k)) >= thresh:
                return (all_cols[col_idx], col_idx)

    return None


def get_political_parties_results(
    pol_parties_column: ColumnTuple,
    pol_parties_results_column: ColumnTuple,
) -> ResultsMap:
    """Returns a dictionary mapping the political parties to their vote count.

    Args:
        pol_parties_column (ColumnTuple): Tuple containing the political parties names column data and its index
        pol_parties_results_column (ColumnTuple): Tuple containing the political parties results column and its index 
 
    Returns:
        dict: A dictionary mapping the political parties names to their corresponding results (vote count)
    """
    results = {}
    pol_parties_column_data = pol_parties_column[0]
    pol_parties_results_column_data = pol_parties_results_column[0]
    pol_parties_results_column_bboxes = [
        cell[1] for cell in pol_parties_results_column_data
    ]
    pol_parties_results_column_values = [
        cell[0] for cell in pol_parties_results_column_data
    ]

    # Loop through each value in the column containing the political parties data
    for value in pol_parties_column_data:
        name = value[0]
        bbox = value[1]

        # Loop through all the bboxes associated with the pol. parties results column data
        for idx in range(len(pol_parties_results_column_bboxes)):
            if is_near(
                bbox[1], pol_parties_results_column_bboxes[idx][1], 8
            ) and is_near(bbox[2], pol_parties_results_column_bboxes[idx][0], 60):
                # Check if the bbox of the pol. party name is opposite the bbox of the result
                value = pol_parties_results_column_values[idx]
                results[name] = int(float(value)) if is_number(value) else None
                break
        else:
            results[name] = None

    # Return the dictionary containing the map of the pol. party names and their results
    return results


def get_polling_unit_data_values_column(
    all_cols: AllColumns,
    polling_unit_data_fields_column: ColumnTuple,
    thresh: Optional[int] = 2,
) -> Union[ColumnTuple, None]:
    """Returns the column containing the polling unit data values.

    Args:
        all_cols (AllColumns): All the columns extracted from the OCR'd image
        polling_unit_data_fields_column (ColumnTuple): Tuple containing the polling unit data fields column data and its index
        thresh (Optional[int]): A heuristic value denoting the minimum number of OCR'd results that must be in the column
    
    Returns:
        tuple: A tuple containing
        - col (ColumnData): Column data
        - col_idx (int): Index of the column in the list of all extracted columns
    """
    if not polling_unit_data_fields_column:
        return None

    polling_unit_data_fields, polling_unit_data_fields_col_idx = (
        polling_unit_data_fields_column[0],
        polling_unit_data_fields_column[1],
    )
    pu_bboxes = [cell[1] for cell in polling_unit_data_fields]

    # Loop through all the columns
    for col_idx, col in enumerate(all_cols):
        if col_idx != polling_unit_data_fields_col_idx:
            col_bboxes = [cell[1] for cell in col]

            # The starting y-coordinates for the bboxes must be close,
            # and the ending-x coordinate of the pu data field bbox must be
            # quite close to the starting x-coordinate of the result figures column bbox we are looking for
            k = map(
                lambda bbox: any(
                    [
                        (
                            is_near(bbox[1], pp_bbox[1], 10)
                            and is_near(bbox[0], pp_bbox[2], 180)
                            and pp_bbox[2] < bbox[0]
                        )
                        for pp_bbox in pu_bboxes
                    ]
                ),
                col_bboxes,
            )

            # Check if the column contains a minimum number of values for the PU data
            # This minimum number is determined by the 'thresh' parameter
            if sum(list(k)) >= thresh:
                return (all_cols[col_idx], col_idx)

    return None


def get_polling_unit_data_results(
    polling_unit_data_fields_column: ColumnTuple,
    polling_unit_data_values_column: ColumnTuple,
) -> ResultsMap:
    """Returns a dictionary mapping the polling unit (PU) data fields to their values.

    Args:
        polling_unit_data_fields_column (ColumnTuple): Tuple containing the polling unit data fields column data and its index
        polling_unit_data_values_column (ColumnTuple): Tuple containing the polling unit data values column and its index

    Returns:
        dict: A dictionary mapping the PU data fields to their corresponding values
    """
    results = {}
    pu_data_fields_column_data = polling_unit_data_fields_column[0]
    pu_data_values_column_data = polling_unit_data_values_column[0]
    pu_data_values_column_bboxes = [cell[1] for cell in pu_data_values_column_data]
    pu_data_values_column_results = [cell[0] for cell in pu_data_values_column_data]

    # Loop through all the values in the PU data fields column
    for value in pu_data_fields_column_data:
        name = value[0]
        bbox = value[1]

        # Loop through all the bboxes associated with the PU data values
        for idx in range(len(pu_data_values_column_bboxes)):
            if is_near(bbox[1], pu_data_values_column_bboxes[idx][1], 10) and is_near(
                bbox[2], pu_data_values_column_bboxes[idx][0], 180
            ):
                # Check if the bbox of the PU data field name is opposite the bbox of the result
                value = pu_data_values_column_results[idx]
                results[name] = int(float(value)) if is_number(value) else None
                break
        else:
            results[name] = None

    # Return the dictionary containing the map of the PU data field names and their results
    return results


def get_election_type(
    all_cols: AllColumns, similarity_thresh: Optional[int] = 0.8
) -> Union[str, None]:
    """Returns the OCR'd election type.

    Args:
        all_cols (AllColumns): All the columns extracted from the OCR'd image
        similarity_thresh (Optional[int]): A heuristic threshold value specifying the minimum similarity index between the OCR'd and actual election type
    
    Returns:
        str: The extracted election type
    """
    # Loop through all the columns
    for col_idx, col in enumerate(all_cols):
        if not col:
            continue

        col_texts = [cell[0] for cell in col]

        # Loop through the election types
        for election_type in ELECTION_TYPES:
            # Loop through all the texts in the column
            for text in col_texts:
                # Check if the text is similar to the election type
                if similar(election_type, text) >= similarity_thresh:
                    return election_type
    else:
        return None


def get_pu_reg_info_fields_column(
    all_cols: AllColumns,
    values_thresh: Optional[int] = 2,
    similarity_thresh: Optional[float] = 0.8,
) -> Union[ColumnTuple, None]:
    """Returns the column containing the PU registration info fields and its index.

    Args:
        all_cols (AllColumns): All the columns extracted from the OCR'd Image
        thresh (Optional[int]): A heuristic threshold value specifying the minimum number of values in the column
        similarity_thresh (Optional[int]): A heuristic threshold value specifying the minimum similarity index between the OCR'd and actual text
    
    Returns:
        tuple: A tuple containing
        - col (Column data): The PU registration fields column data
        - col_idx (int): Index of the column in the list of all extracted columns
    """
    # Loop through all the columns
    for col_idx, col in enumerate(all_cols):
        if not col:
            continue
        count = 0
        out = []

        # List of the texts in the current column
        col_values = [cell[0] for cell in col]

        # Loop through all the polling unit data fields
        for field in POLLING_UNIT_REGISTRATION_INFO_FIELDS:
            # Loop through all the texts for this column
            for value_idx, value in enumerate(col_values):
                # Check if the cell value is similar to any of the PU reg info fields
                if similar(field, value) > similarity_thresh:
                    count += 1
                    out.append((field, col[value_idx][1]))
                    continue

        # Check if the number of values in the column is greater than the specified threshold
        if count > values_thresh:
            return (out, col_idx)

    return None


def get_pu_reg_info_values_column(
    all_cols: AllColumns,
    pu_reg_info_fields_column: ColumnTuple,
    thresh: Optional[int] = 2,
) -> Union[ColumnTuple, None]:
    """Returns the column containing the pu registration info values and its index.

    Args:
        all_cols (AllColumns): All the columns extracted from the OCR'd image
        pu_reg_fields_column (ColumnTuple): A tuple containing the PU registration fields column and its index
        thresh (Optional[int]): A heuristic threshold value  specifying the minimum number of texts in the column

    Returns:
        tuple: A tuple containing
        - col (ColumnData): PU registration column data
        - col_idx (int): Index of the column in the list of all extracted columns
    """
    if not pu_reg_info_fields_column:
        return None

    pu_reg_info_fields, pu_reg_info_fields_col_idx = (
        pu_reg_info_fields_column[0],
        pu_reg_info_fields_column[1],
    )
    pu_reg_info_bboxes = [cell[1] for cell in pu_reg_info_fields]

    # Loop through all the columns
    for col_idx, col in enumerate(all_cols):
        if col_idx != pu_reg_info_fields_col_idx:
            col_bboxes = [cell[1] for cell in col]

            # The starting y-coordinates for the bboxes must be close,
            # and the ending-x coordinate of the pu data field bbox must be
            # quite close to the starting x-coordinate of the result figures column bbox we are looking for
            k = map(
                lambda bbox: any(
                    [
                        (
                            is_near(bbox[1], pu_reg_info_bbox[1], 10)
                            and is_near(bbox[0], pu_reg_info_bbox[2], 180)
                            and pu_reg_info_bbox[2] < bbox[0]
                        )
                        for pu_reg_info_bbox in pu_reg_info_bboxes
                    ]
                ),
                col_bboxes,
            )

            # Check if the column contains a minimum number of values for the PU reg info
            # This minimum number is determined by the 'thresh' parameter
            if sum(list(k)) >= thresh:
                return (all_cols[col_idx], col_idx)

    return None


def get_pu_reg_info_results(
    pu_reg_info_fields_column: ColumnTuple,
    pu_reg_info_values_column: ColumnTuple,
) -> ResultsMap:
    """Returns a dictionary mapping the PU registration info fields to their values.

    Args:
        pu_reg_info_fields_column (ColumnTuple): Tuple containing the PU registration info column data and its index
        pu_reg_info_values_column (ColumnTuple): Tuple column containing the PU registration info values column data and its index 

    Returns:
        dict: A dictionary mapping the PU registration info fields to their values
    """
    results = {}
    pu_reg_info_fields_column_data = pu_reg_info_fields_column[0]
    pu_reg_info_values_column_data = pu_reg_info_values_column[0]
    pu_reg_info_values_column_bboxes = [
        cell[1] for cell in pu_reg_info_values_column_data
    ]
    pu_reg_info_values_column_results = [
        cell[0] for cell in pu_reg_info_values_column_data
    ]

    # Loop through all the values in the PU data fields column
    for value in pu_reg_info_fields_column_data:
        name = value[0]
        bbox = value[1]

        # Loop through all the bboxes associated with the PU reg info results column data
        for idx in range(len(pu_reg_info_values_column_bboxes)):
            if is_near(
                bbox[1], pu_reg_info_values_column_bboxes[idx][1], 10
            ) and is_near(bbox[2], pu_reg_info_values_column_bboxes[idx][0], 180):
                # Check if the bbox of the PU reg info field name is opposite the bbox of the result
                value = pu_reg_info_values_column_results[idx]
                results[name] = value
                break
        else:
            results[name] = None

    # Return the dictionary containing the map of the PU reg info fields to their values
    return results


def get_document_data(
    all_cols: AllColumns,
) -> Tuple[
    Union[ResultsMap, None],
    Union[ResultsMap, None],
    str,
    Union[ResultsMap, None],
]:
    """Full pipeline for parsing the INEC document and returning the results.

    Args:
        all_cols: All the columns extracted from the image

    Returns:
        tuple: A tuple containing
        - ResultsMap: Political parties vote results
        - ResultsMap: Polling unit data results
        - str: Election type
        - ResultsMap: Polling unit registration info results
    """
    # Get the political parties results data
    political_parties_column = get_political_parties_column(all_cols)
    pol_parties_results_column = get_political_parties_results_column(
        all_cols, political_parties_column
    )
    pol_parties_results = (
        get_political_parties_results(
            political_parties_column, pol_parties_results_column
        )
        if pol_parties_results_column
        else None
    )

    # Get the polling unit data
    polling_unit_data_fields_column = get_polling_unit_data_fields_column(all_cols)
    pu_data_values_column = get_polling_unit_data_values_column(
        all_cols, polling_unit_data_fields_column
    )
    pu_data_results = (
        get_polling_unit_data_results(
            polling_unit_data_fields_column, pu_data_values_column
        )
        if pu_data_values_column
        else None
    )

    # Get the PU reg info data
    pu_reg_info_fields_column = get_pu_reg_info_fields_column(all_cols)
    pu_reg_info_values_column = get_pu_reg_info_values_column(
        all_cols, pu_reg_info_fields_column
    )
    pu_reg_info_results = (
        get_pu_reg_info_results(pu_reg_info_fields_column, pu_reg_info_values_column)
        if pu_reg_info_values_column
        else None
    )

    # Get the election type
    election_type = get_election_type(all_cols)

    return (
        pol_parties_results,
        pu_data_results,
        election_type,
        pu_reg_info_results
    )


def order_points(points: np.ndarray) -> np.ndarray:
    """Re-order (sort) the coordinates of the document's contour.

    Args:
        points (np.ndarray): The points on the document's contour

    Returns:
        np.ndarray: The sorted points
    """
    # Sort the points based on their x-coordinates
    x_sorted = points[np.argsort(points[:, 0]), :]

    # Grab the left-most and right-most points from the sorted
    # x-coordinate points
    left_most = x_sorted[:2, :]
    right_most = x_sorted[2:, :]

    # Now, sort the left-most coordinates according to their
    # y-coordinates so we can grab the top-left and bottom-left
    # points, respectively
    left_most = left_most[np.argsort(left_most[:, 1]), :]
    (tl, bl) = left_most

    # Now that we have the top-left coordinate, use it as an
    # anchor to calculate the Euclidean distance between the
    # top-left and right-most points; by the Pythagorean
    # theorem, the point with the largest distance will be
    # our bottom-right point
    D = dist.cdist(tl[np.newaxis], right_most, "euclidean")[0]
    (br, tr) = right_most[np.argsort(D)[::-1], :]

    # Return the coordinates in top-left, top-right,
    # bottom-right, and bottom-left order
    return np.array([tl, tr, br, bl], dtype="float32")


def four_point_transform(image: np.ndarray, points: np.ndarray) -> np.ndarray:
    """Obtains a bird's eye view of a document in an image using four point transform algorithm.

    Args:
        image (np.ndarray): The input image
        pts (np.ndarray): The four points of the document

    Returns:
        np.ndarray: The transformed image
    """
    # Obtain a consistent order of the points and unpack them
    rect = order_points(points)
    (tl, tr, br, bl) = rect

    # Compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordinates or the top-right and top-left x-coordinates
    width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    max_width = max(int(width_a), int(width_b))

    # Compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    max_height = max(int(height_a), int(height_b))

    # Construct the destination points which will be used to
    # map the screen to a top-down, "birds-eye" view
    dst = np.array(
        [
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1],
        ],
        dtype="float32",
    )

    # Compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (max_width, max_height))

    # Return the warped/transformed image
    return warped
