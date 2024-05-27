#
#       Synthetic Patients Dockerfile
#
# To build docker image, use the following command:
# docker buildx create --name multiplatform-builder
# docker buildx use multiplatform-builder
# docker buildx inspect --bootstrap
# docker buildx build --platform linux/amd64,linux/arm64 -t syntheticpatients/base:latest --output=type=registry
#
#
# To RUN the docker image, use the following command:
# /bin/sh code/run.sh
# which will run
# docker run -it -p 5000:5000 --entrypoint="/home/sp/code/start.sh" --rm synpt/base && open http://localhost:5000
#
#




# Start with basic ubuntu image
FROM ubuntu:focal-20240427

MAINTAINER Alex Goodell <alexgoodell@gmail.com>

# Install basics
RUN apt-get update && apt-get install -y git make wget curl bison vim fish

# Install python dependencies
RUN apt-get update && apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev

# Install audio dependencies
#RUN apt-get install -y --no-install-recommends alsa-base alsa-utils libsndfile1-dev

# sci py dependencies
RUN apt-get update && apt-get install -y libblas-dev liblapack-dev libatlas-base-dev gfortran

# Install ffmpeg
ENV DEBIAN_FRONTEND="noninteractive" TZ="Europe/London"
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

# Create a directory for downloads
RUN mkdir /home/downloads
WORKDIR /home/downloads

# install python 3.11
RUN wget https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tgz
RUN tar -xf Python-3.11.0.tgz
WORKDIR /home/downloads/Python-3.11.0
RUN ./configure --enable-optimizations
RUN make -j$(nproc)
RUN make altinstall

# Set python 3.11 as the default python
RUN ln -s /usr/local/bin/python3.11 /usr/bin/python

# Get pip (python package manager)
RUN cd /home/downloads && wget https://bootstrap.pypa.io/get-pip.py
RUN cd /home/downloads && python get-pip.py
RUN pip install --upgrade pip

# Install poetry (improved python package manager)
RUN pip install poetry

# Set the working directory
WORKDIR /home/sp/code

# Copy the poetry files and install the dependencies
COPY code/pyproject.toml code/poetry.lock /home/sp/code/
RUN POETRY_VIRTUALENVS_CREATE=false poetry install

# Install python package keyboard (needed by wav2lip; unlear why poetry doesn't fix this)
RUN apt-get update && apt-get install -y kmod kbd
RUN pip install keyboard


# Audio dependencies
## ffmpeg payer dependencies (inactive)
#apt install ffmpeg libavcodec-dev libavdevice-dev libavfilter-dev libavformat-dev \
#libavutil-dev libswscale-dev libswresample-dev libpostproc-dev libsdl2-dev libsdl2-2.0-0 \
#libsdl2-mixer-2.0-0 libsdl2-mixer-dev python3-dev

#    RUN apt-get install -y pulseaudio
#    # Install the python dependencies
#    RUN apt install -y python3-pyaudio portaudio19-dev
#    ENV PULSE_SERVER host.docker.internal \
#    RUN pulseaudio --system -D


# Copy the current directory into the container
COPY --link . /home/sp

WORKDIR /home/sp/code
RUN chmod 777 start.sh


# wave2lip has a broken dependency that needs manual replacement of one file
COPY code/docker/decorators.py /usr/local/lib/python3.11/site-packages/librosa/util/decorators.py

# Set the default shell to fish
ENTRYPOINT ["/home/sp/code/start.sh"]

