FROM python:3.12.4-bookworm
RUN pip install --no-cache-dir pytest==8.3.5
WORKDIR /app
COPY app/ /app/
COPY private_setup.py /tmp/private_setup.py
RUN python3 /tmp/private_setup.py && rm /tmp/private_setup.py
