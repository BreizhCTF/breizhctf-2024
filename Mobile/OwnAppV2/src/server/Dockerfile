FROM python:3.8-alpine

WORKDIR /app

RUN pip3 install flask

COPY . .

ENTRYPOINT ["python3","/app/serv.py"]
