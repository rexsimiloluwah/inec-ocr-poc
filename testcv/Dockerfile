FROM python:3.10-slim-bullseye

RUN apt-get update \
  && apt-get install -y --no-install-recommends --no-install-suggests \
  build-essential \
  libgl1 \
  libglib2.0-0 \
  && pip install --no-cache-dir --upgrade pip

WORKDIR /app 

RUN pip install --no-cache-dir opencv-python==4.6.0.66

COPY . /app 

CMD ["python","script.py"]

