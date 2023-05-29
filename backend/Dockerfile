FROM python:3.7-alpine

COPY . /backend
WORKDIR /backend
RUN pip install -r requirements.txt

EXPOSE 5000
ENTRYPOINT [ "python", "app.py" ]