FROM python:3.11-alpine

RUN python3 -m pip install mythic-container

WORKDIR /Mythic/

COPY [".", "."]

CMD ["python3", "main.py"]