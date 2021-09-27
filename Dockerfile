FROM python:3.8.5-slim-buster
COPY ./app /app
WORKDIR /app
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
EXPOSE 8000
