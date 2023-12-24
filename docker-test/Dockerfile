FROM python:3.11-slim
#"ls -lha && echo josh && pip install --no-cache -r /asset-input/requirements.txt -t /asset-output/python && git clone https://github.com/geudrik/peloton-client-library.git /asset-output/python/peloton"
# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./requirements.txt /app
RUN apt-get update
RUN apt-get install -y git
# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt
RUN git clone https://github.com/geudrik/peloton-client-library.git
RUN pip install peloton-client-library/
RUN pip install ipython
COPY . /app
ENV AWS_DEFAULT_PROFILE home
