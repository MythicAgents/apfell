FROM python:3.11-bookworm as build

COPY [".docker/requirements.txt", "requirements.txt"]
RUN python3 -m pip install --user -r requirements.txt


# "Default" stage:
FROM python:3.11-alpine

# Copy generated site-packages from former stage:
COPY --from=build /root/.local /root/.local
COPY --from=build /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

WORKDIR /Mythic/

COPY [".", "."]

CMD ["python3", "main.py"]