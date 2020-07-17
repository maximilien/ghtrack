# Use the official Python image to create a build artifact.
# This is based on Debian and sets the GOPATH to /go.
# https://hub.docker.com/_/python
FROM python:3 as builder

# Make ghtrack directory
RUN mkdir /ghtrack

# Copy local code to the container image.
COPY *.py /ghtrack/
COPY ght /ghtrack/
COPY README.md /ghtrack/
COPY LICENSE /ghtrack/
COPY Dockerfile /ghtrack/
COPY hack/ /ghtrack/hack/
COPY test/ /ghtrack/test/

# Insall dependencies via pip.
RUN pip install PyGitHub==1.51
RUN pip install PyYAML==5.3.1
RUN pip install docopt==0.6.2

# Build and run UTs
RUN /ghtrack/hack/build.sh --tests

# Run sanity check.
CMD /ghtrack/ght --version