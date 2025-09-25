FROM ubuntu:22.04

RUN apt update &&\
    apt upgrade -y

RUN apt update && apt install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa &&\
    apt-get update &&\
    apt-get -y install python3.10

RUN apt install -y python3-pip
RUN python3.10 -m pip install --upgrade setuptools
RUN python3.10 -m pip install --upgrade pip

RUN apt install -y python3-pip
RUN apt install -y build-essential
RUN apt -y install curl python-is-python3
RUN apt -y install uvicorn

COPY . .

#RUN poetry install
RUN python3.10 -m pip install .

EXPOSE 80

ENTRYPOINT ["uvicorn", "src.llm_server.main:app", "--host", "0.0.0.0", "--port", "80"]
#CMD ["/bin/bash"]