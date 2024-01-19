FROM python:3.11-alpine

RUN pip3 install mythic-container

WORKDIR /Mythic/

COPY [".", "."]

CMD ["python3", "main.py"]