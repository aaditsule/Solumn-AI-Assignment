FROM python:3.12.4-slim-bookworm@sha256:a3e58f9399353be051735f09be0316bfdeab571a5c6a24fd78b92df85bcb2d85

RUN pip install --no-cache-dir pytest==8.3.5

WORKDIR /app
COPY app/ /app/
COPY sink.py /opt/rle/grading/sink.py
COPY start.sh /opt/rle/start.sh
COPY private_setup.py /tmp/private_setup.py
RUN python3 /tmp/private_setup.py \
    && rm -f /tmp/private_setup.py \
    && mkdir -p /var/log/rle /logs/verifier \
    && chmod 0755 /opt/rle/start.sh

ENTRYPOINT ["/opt/rle/start.sh"]
