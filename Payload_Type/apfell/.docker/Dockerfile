FROM python:3.11-slim

RUN python3 -m pip install mythic-container

WORKDIR /Mythic/

COPY [".", "."]

CMD ["python3", "main.py"]