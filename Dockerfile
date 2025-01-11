FROM python:3.12-slim as python_3_12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ=Asia/Baku

RUN apt-get update --allow-releaseinfo-change
RUN apt-get install nano iputils-ping curl gettext -y

FROM python_3_12 as app_enviroment

# create folers
RUN mkdir -p /home/code
RUN mkdir -p /home/cache
RUN mkdir -p /home/storage
RUN mkdir -p /home/logs

# copy requirements and install
COPY ./requirements.txt /home/code/requirements.txt
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r /home/code/requirements.txt --verbose

FROM app_enviroment as app

# copy code
WORKDIR /home/code/
COPY . .

RUN chmod +x ./entrypoint.sh
