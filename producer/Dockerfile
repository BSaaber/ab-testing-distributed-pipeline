FROM python:3.11
COPY requirements.txt .
RUN pip install --user -r requirements.txt

copy producer.py .
CMD [ "python", "./producer.py"]