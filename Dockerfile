FROM python:3.10

RUN \
  apt-get update \
  && apt-get install -y wget \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir /publicdb
WORKDIR /publicdb

# Install miniconda
RUN \
  wget --no-verbose https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh \
  && bash miniconda.sh -b -p /opt/miniconda;

# Use conda Python
ENV PATH /opt/miniconda/bin:$PATH

# Update Python package managers
RUN pip install --no-cache-dir --upgrade pip
RUN conda update --yes conda

# Install requirements
COPY provisioning/roles/publicdb/files/conda.list ./
RUN conda install --yes --file conda.list

COPY provisioning/roles/publicdb/files/pip.list ./
RUN pip install --no-cache-dir -r pip.list

COPY requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt
