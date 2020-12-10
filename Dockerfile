FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive

# http://bugs.python.org/issue19846
# At the moment, setting "LANG=C" on a Linux system fundamentally breaks
# Python 3.
ENV LANG C.UTF-8

# Install dependencies.
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    gifsicle \
    git \
    python3-venv \
    wget \
  && apt-get clean autoclean \
  && apt-get autoremove -y \
  && rm -rf /var/lib/apt/lists/* \
  && rm -f /var/cache/apt/archives/*.deb

RUN python3 -m venv /env

# Set virtualenv environment variables. This is equivalent to running
# source /env/bin/activate
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

ADD . /ssite/

RUN pip install /ssite/
WORKDIR /workspace

ENTRYPOINT ["ssite"]