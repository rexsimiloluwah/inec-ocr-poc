<center>
<h1>INER OCR APP 🇳🇬</h1>
<p>A POC application for performing OCR on INEC statement of result images</p>
</center>

## Introduction

## Uses
- Python 
- [PaddleOCR]() - OCR Engine 
- [FastAPI]()
- Docker 
- k8s

## How it works?

## Requirements
- Python 3.x 

## To run the application locally
1. Clone the repository
```bash
$ git clone https://github.com/rexsimiloluwah/inec-ocr-poc.git 
$ cd inec-ocr-poc
```

2. Setup a virtual environment 
```bash
# using virtualenv
$ python -m venv env 
$ source env/bin/activate
```

3. Install the dependencies from `requirements.txt`
```bash
$ pip install -r requirements.txt
```

4. Run the web server 
```bash
$ uvicorn src.web.main:app --reload

# using make
$ make start-web
```

## To run the application using Docker
```bash
$ docker pull similoluwaokunowo/inec-ocr-app
$ docker run -p 8040:8040 similoluwaokunowo/inec-ocr-app
```

## Testing the application

