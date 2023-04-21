#!/usr/bin/env python

"""main.py: The entry point for the server."""

__author__ = "Similoluwa Okunowo"
__email__ = "rexsimiloluwa@gmail.com"

import os
import io
import uuid
from pathlib import Path

import cv2
from PIL import Image
from fastapi.exceptions import HTTPException
from fastapi import FastAPI, Request, Depends, UploadFile, File, Header
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from .utils import (
    fetch_details,
    handle_file_upload,
    write_img_to_tmp,
    upload_img_to_cloudinary,
)
from .logger import logger
from ..inec_ocr.common import show_image
from ..inec_ocr.clustering import cluster_ocr_results
from ..inec_ocr.document import get_document_data
from ..inec_ocr.ocr import (
    extract_text,
    draw_ocr,
    filter_text_predictions,
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


@app.post("/inec-ocr")
async def inec_ocr(file: UploadFile = File(...), full: bool = True):
    def file_handler(p: Path):
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

        results = {
            "output_image_url": upload_url,
            "political_parties_vote_results": pol_parties_results,
            "pu_data_results": pu_data_results,
            "pu_reg_info_results": pu_reg_info_results,
            "election_type": election_type,
        }

        if full:
            results["raw_ocr_results"] = {"bboxes": bboxes, "scores": scores, "texts": texts}

        logger.info(f"Successfully computed results: {results}")
        return results

    response = handle_file_upload(file, file_handler)

    return response
