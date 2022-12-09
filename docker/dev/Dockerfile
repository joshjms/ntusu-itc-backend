FROM python:3.10.4-slim-buster
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /project
COPY requirements.txt /project/
RUN pip install -r requirements.txt
COPY . /project/
