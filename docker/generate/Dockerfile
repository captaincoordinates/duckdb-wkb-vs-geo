FROM python:3.12-slim

COPY src/generate/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY src/generate/generate_data.py /app.py
