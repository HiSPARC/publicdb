FROM python:3.12

# hadolint ignore=DL3008
RUN \
  apt-get update \
  && apt-get install -y --no-install-recommends wget \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir /publicdb
WORKDIR /publicdb

# Install miniconda
RUN \
  wget --no-verbose https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh \
  && bash miniconda.sh -b -p /opt/miniconda;

# Use conda Python
ENV PATH /opt/miniconda/bin:$PATH

# Update and configure Python package managers
ENV PIP_NO_CACHE_DIR 1
ENV PIP_PROGRESS_BAR off
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
RUN conda update --yes conda

# Install requirements
COPY provisioning/roles/publicdb/files/requirements-conda.txt ./
RUN conda install --yes --file requirements-conda.txt

COPY provisioning/roles/publicdb/files/requirements-pip.txt ./
RUN pip install -r requirements-pip.txt

COPY requirements-dev.txt ./
RUN pip install -r requirements-dev.txt
