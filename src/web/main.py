#!/usr/bin/env python

"""main.py: The entry point for the server."""

import uuid
from pathlib import Path
from typing import NamedTuple

import cv2
from fastapi import Depends, FastAPI, File, Header, Request, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image

from ..inec_ocr.clustering import cluster_ocr_results
from ..inec_ocr.common import show_image
from ..inec_ocr.document import get_document_data
from ..inec_ocr.ocr import draw_ocr, extract_text, filter_text_predictions
from ..inec_ocr.types import OCRResultType, ResultsMap
from .logger import logger
from .utils import (
    fetch_details,
    handle_file_upload,
    upload_img_to_cloudinary,
    write_img_to_tmp,
)

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = str(BASE_DIR / "templates")
STATIC_FILES_DIR = str(BASE_DIR / "static")
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

app = FastAPI()

# Mount the static files dir
app.mount("/static", StaticFiles(directory=STATIC_FILES_DIR), name="static")

# Templates dir
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get("/", response_class=HTMLResponse)
def home_view(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/healthcheck")
def healthcheck():
    return {"status": True, "message": "Server is healthy!"}


class UploadHandlerResponse(NamedTuple):
    upload_url: str
    pol_parties_results: ResultsMap
    pu_data_results: ResultsMap
    election_type: str
    pu_reg_info_results: ResultsMap
    raw_ocr_results: OCRResultType


def upload_handler(p: Path) -> UploadHandlerResponse:
    """File upload handler for the OCR endpoint."""
    logger.debug("started computing results...")
    # Load the image
    image = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
    # Obtain the OCR results
    bboxes, texts, scores = extract_text(str(p))
    filtered_bboxes, filtered_texts = filter_text_predictions(bboxes, texts, scores)

    # Cluster the OCR results
    final_cols = cluster_ocr_results(filtered_bboxes, filtered_texts)

    # Obtain the results
    (
        pol_parties_results,
        pu_data_results,
        election_type,
        pu_reg_info_results,
    ) = get_document_data(final_cols)

    # Handle saving the annotated image to cloudinary
    annotated_img = draw_ocr(image, bboxes)

    # Write the annotated image to a tmp path
    tmp_path = write_img_to_tmp(annotated_img)

    # Save the image to cloudinary
    upload_url = upload_img_to_cloudinary(tmp_path)

    return (
        upload_url,
        pol_parties_results,
        pu_data_results,
        election_type,
        pu_reg_info_results,
        (bboxes, texts, scores),
    )


@app.post("/inec-ocr")
async def inec_ocr(file: UploadFile = File(...), full: bool = True):
    # Obtain the response
    response = handle_file_upload(file, upload_handler)

    if not response["status"]:
        raise HTTPException(status_code=400, detail=response["error"])

    data = response["data"]
    results = {
        "output_image_url": data[0],
        "political_parties_vote_results": data[1],
        "pu_data_results": data[2],
        "pu_reg_info_results": data[4],
        "election_type": data[3],
    }

    if full:
        results["raw_ocr_results"] = {
            "bboxes": data[5][0],
            "scores": data[5][1],
            "texts": data[5][2],
        }

    logger.info(f"Successfully computed results: {results}")
    return {"status": True, "data": results}
