#!/usr/bin/env python

"""clustering.py: Contains the algorithm for agglomerative clustering of the OCR'd bboxes"""

__author__ = "Similoluwa Okunowo"
__email__ = "rexsimiloluwa@gmail.com"
__credits__ = [
    "Adrian Rosebrock (for suggesting the agglomerative clustering algorithm)"
]

from typing import List

import numpy as np
from sklearn.cluster import AgglomerativeClustering

from .types import AllColumns, OCRBBoxesResultType, OCRTextsResultType


def get_clustering_model() -> AgglomerativeClustering:
    """Returns the agglomerative clustering model.

    Agglomerative clustering is a hierarchical clustering method.
    This starts each data point (bounding box) as its own cluster and gradually
    merges the most similar clusters together until a particular stopping criterion is met.
    The agglomerative clustering algorithm will be used to cluster the bounding boxes for the extracted text
    into their respective columns
    """
    model = AgglomerativeClustering(
        n_clusters=None, affinity="manhattan", linkage="complete", distance_threshold=30
    )

    return model


def cluster_ocr_results(
    bboxes: OCRBBoxesResultType,
    texts: OCRTextsResultType,
) -> AllColumns:
    """Returns the results of clustering the bounding boxes.

    This essentially clusters the obtained bounding boxes of the localized texts into columns.
    The algorithm is based on the assumption that texts in the same column will have a similar
    starting x-coordinate value.

    Args:
        bboxes (OCRBBoxesResultType): The bounding boxes associated with the extracted texts
        texts (OCRTextsResultType): The extracted texts

    Returns:
        list: A list containing the clustered columns.
    """
    # Generate the input data for the clustering model
    # A tuple containing the starting x-coordinate and a trivial y dimension
    input = [(c[0], 0) for c in bboxes]

    model = get_clustering_model()

    # Fit the HAC model
    model.fit(input)

    clusters = []

    # Loop over all the clusters
    for label in np.unique(model.labels_):
        # Extract the indexes for the coords belonging to the current cluster
        idxs = np.where(model.labels_ == label)[0]

        # Verify that the cluster is sufficiently large
        # The minimum size of the cluster is heuristically chosen to be the expected least amount of elements in each column
        if len(idxs) > 1:
            # Compute the average of the starting x-coordinates of elements in the cluster
            avg_x_coord = np.average([bboxes[i][0] for i in idxs])
            clusters.append((label, avg_x_coord))

    # Sort the clusters based on the computed average of the x-coordinates
    sorted_clusters = sorted(clusters, key=lambda x: x[1])

    final_cols = []

    # Arrange the extracted texts into their respective columns
    for label, _ in sorted_clusters:
        # Extract the indexes for the coordinates belonging to the current cluster
        idxs = np.where(model.labels_ == label)[0]

        # Extract the starting y-coordinate from the elements in the current cluster
        y_coords = [bboxes[i][1] for i in idxs]
        sorted_idxs = idxs[np.argsort(y_coords)]

        # Create a list of the texts in the column and their associated bounding boxes
        cols = [(texts[i].strip(), bboxes[i]) for i in sorted_idxs]
        final_cols.append(cols)

    return final_cols
