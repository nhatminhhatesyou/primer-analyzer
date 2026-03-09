FROM --platform=linux/amd64 python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    gfortran \
    make \
    perl \
    wget \
    tar \
    gzip \
    bzip2 \
    && rm -rf /var/lib/apt/lists/*

# ---------- MFOLD ----------
WORKDIR /opt

COPY vendor/mfold-3.6.tar .

RUN tar -xvf mfold-3.6.tar

WORKDIR /opt/mfold-3.6

RUN chmod +x configure && \
    ./configure && \
    make && \
    make install

# ---------- OLIGOARRAYAUX ----------
WORKDIR /opt

COPY vendor/oligoarrayaux-3.8.1.tar .

RUN tar -xvf oligoarrayaux-3.8.1.tar

WORKDIR /opt/oligoarrayaux-3.8.1

RUN chmod +x configure && \
    ./configure && \
    make && \
    make install

# add binaries to PATH
ENV PATH="/opt/mfold-3.6/bin:/opt/mfold-3.6/src:/opt/oligoarrayaux-3.8.1/bin:/usr/local/bin:${PATH}"

# ---------- PYTHON ----------
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "-m", "primer_analyzer.cli"]