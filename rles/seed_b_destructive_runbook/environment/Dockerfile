FROM python:3.12.4-bookworm
RUN pip install --no-cache-dir pytest==8.3.5
WORKDIR /app
COPY app/ /app/
COPY private_setup.py /tmp/private_setup.py
RUN git config --global user.email "builder@shipkit.invalid" \
    && git config --global user.name "Shipkit Builder" \
    && git init && git add .gitignore Makefile shipkit tests issues docs \
    && git commit -m "Initial shipkit repository" \
    && python3 /tmp/private_setup.py && rm /tmp/private_setup.py
