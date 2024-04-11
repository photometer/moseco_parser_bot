FROM python:3.8-slim
ENV PYTHONUNBUFFERED=1
RUN mkdir /app
COPY requirements.txt /app
RUN python -m pip install --upgrade pip
RUN pip3 install -r /app/requirements.txt --no-cache-dir
COPY . /app
WORKDIR /app/moseco/moseco