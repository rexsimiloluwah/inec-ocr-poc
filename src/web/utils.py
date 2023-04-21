#!/usr/bin/env python

"""utils.py: Contains utility functions using by the FastAPI-powered web app/API"""

__author__ = "Similoluwa Okunowo"
__email__ = "rexsimiloluwa@gmail.com"

import shutil
import socket
from datetime import datetime
from pathlib import Path
from typing import Tuple, Callable, Union
from tempfile import NamedTemporaryFile

import cv2
import numpy as np
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, Header, Depends
from fastapi.exceptions import HTTPException

from .settings import get_settings, Settings

settings = get_settings()

# Initialize cloudinary
cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_secret_key,
    secure=True,
)


def save_upload_file(upload_file: UploadFile, dest_path: Path) -> None:
    """Saves the uploaded file to a specific destination.

    Args:
        upload_file (UploadFile): Uploaded file (via the request form data)
        dest_path (Path): Destination path for saving the uploaded file
    """
    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()


def save_upload_file_to_tmp(upload_file: UploadFile) -> Path:
    """Save the uploaded file to a temporary file path.

    Args:
        upload_file (UploadFile): Uploaded file (via the request form data)

    Returns:
        tmp_path (Path): The temporary file path where the uploaded file was saved
    """
    try:
        suffix = Path(upload_file.filename).suffix
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(upload_file.file, tmp)
            tmp_path = Path(tmp.name)
    finally:
        upload_file.file.close()

    # Return the temporary file path
    return tmp_path


def write_img_to_tmp(img: np.ndarray) -> Path:
    """Write an image to a temporary file path using cv2.

    Args:
        img (np.ndarray): The input image

    Returns:
        tmp_path (Path): The temporary file path where the image was written
    """
    suffix = f"{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.png"
    with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        cv2.imwrite(tmp.name, img)
        tmp_path = Path(tmp.name)

    return tmp_path


def upload_img_to_cloudinary(tmp_path: Path) -> Union[str, None]:
    """Upload an image to cloudinary using the cloudinary SDK.
    
    Args:
        tmp_path (Path): The temporary path to the input image

    Returns:
        upload_url (str): The URL of the uploaded image on cloudinary
    """
    try:
        response = cloudinary.uploader.upload(
            str(tmp_path),
            folder="inec-ocr-images",
            public_id=datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
            overwrite=True,
            resource_type="image",
        )
        return response["url"]
    except Exception as e:
        return None
    finally:
        tmp_path.unlink()


def handle_file_upload(
    upload_file: UploadFile, handler: Callable[[Path], None]
) -> None:
    """A utility function for handling file upload requests.

    Args:
        upload_file (UploadFile): Uploaded file (via the request form data)
        handler (Callable): A callback handler for processing the uploaded file
    """
    tmp_path = save_upload_file_to_tmp(upload_file)
    callback_response = None
    try:
        # Process the file with the handler callback
        callback_response = handler(tmp_path)
        return {"status": True, "data": callback_response}
    except Exception as e:
        return {"status": False, "error": f"An error occurred: {str(e)}"}
    finally:
        # Delete the tmp file
        tmp_path.unlink()


def verify_auth(authorization=Header(None), settings: Settings = Depends(get_settings)):
    if settings.skip_auth:
        return
    if authorization is None:
        raise HTTPException(detail="Unauthorized", status_code=401)
    token_split = authorization.split(" ")
    if len(token_split) != 2:
        raise HTTPException(detail="Invalid token header structure", status_code=401)
    if token_split[1] != settings.app_auth_token:
        raise HTTPException(detail="Invalid token", status_code=401)


def fetch_details() -> Tuple[str, str]:
    hostname = socket.gethostname()
    host_ip = socket.gethostbyname(hostname)
    return str(hostname), str(host_ip)
