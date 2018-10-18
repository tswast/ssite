FROM python:3.6

RUN python -m venv /env

# Set virtualenv environment variables. This is equivalent to running
# source /env/bin/activate
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

ADD . /ssite/

RUN pip install /ssite/
WORKDIR /workspace

ENTRYPOINT ["ssite"]