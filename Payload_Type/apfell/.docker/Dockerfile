FROM python:3.11-bookworm as build

RUN python3 -m pip install mythic-container

# "Default" stage:
FROM python:3.11-alpine

# Copy generated site-packages from former stage:
COPY --from=build /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

WORKDIR /Mythic/

COPY [".", "."]

CMD ["python3", "main.py"]