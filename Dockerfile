FROM python:3.10-slim-bullseye

RUN apt-get update \
  && apt-get install -y --no-install-recommends --no-install-suggests \
  build-essential \
  make \
  gcc \
  libsm6 \
  libxrender1 \ 
  libfontconfig1 \ 
  libice6 \
  libgl1 \
  libglib2.0-0 \
  && pip install --no-cache-dir --upgrade pip

WORKDIR /app 

COPY ./requirements.txt /app

RUN pip install  --requirement /app/requirements.txt 

COPY . /app 

ENV PORT=8040

EXPOSE 8040

RUN chmod +x ./start-web.sh

CMD ["./start-web.sh"]

