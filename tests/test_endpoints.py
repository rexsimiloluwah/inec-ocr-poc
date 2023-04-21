import os
import io
import time
import shutil
import pathlib

from fastapi.testclient import TestClient
from PIL import Image, ImageChops

from src.web.main import app, UPLOADS_DIR

client = TestClient(app)

def test_get_homepage():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_get_healthcheck():
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"status":True,"message":"Server is healthy!"}

def test_ocr_endpoint():
    test_images_path = pathlib.Path("./test-images")
    valid_test_image = os.path.join(test_images_path, "./inec-form-ppocr-test-1.jpeg")
    response = client.post("/inec-ocr", files={"file": open(valid_test_image, "rb")})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    responseBody = response.json()
    assert responseBody["status"] == True
    assert responseBody["data"] != None

# def test_img_upload():
    # valid_image_extensions = ['png','jpeg','jpg']
    # test_images = pathlib.Path("./test-images")
    # for path in test_images.glob("*"):
        # try:
            # img = Image.open(path)
        # except:
            # img = None
        # response = client.post("/img-upload",files={"file":open(path,'rb')})
        # fext = str(path.suffix).replace('.',"")

        # if img:
            # # when the image is valid 
            # assert response.status_code == 200
            # r_stream = io.BytesIO(response.content)
            # echo_img=Image.open(r_stream)

            # # get the difference between the returned image and the original upload image 
            # difference = ImageChops.difference(echo_img,img).getbbox()
            # assert difference is None
        # else:
            # assert response.status_code == 400

    # # remove the uploads directory 
    # time.sleep(3)
    # shutil.rmtree(UPLOADS_DIR)

