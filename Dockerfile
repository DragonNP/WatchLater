FROM python:3.9-slim

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY const_variables.py .
COPY database.py .
COPY main.py .

CMD ["python", "./main.py"]