FROM python:3.11-slim-bookworm

COPY [".docker/requirements.txt", "requirements.txt"]
RUN python3 -m pip install --no-cache-dir -r requirements.txt

WORKDIR /Mythic/

COPY [".", "."]

CMD ["python3", "main.py"]