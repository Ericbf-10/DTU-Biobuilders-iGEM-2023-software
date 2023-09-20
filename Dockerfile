# Use a base image as a starting point
FROM ubuntu:20.04

# Install Miniconda
RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -b -p /miniconda
ENV PATH=$PATH:/miniconda/condabin:/miniconda/bin

# Install required packages into the 'myenv' environment using pip
RUN pip install viennarna==2.6.3
RUN pip install rna==0.11.0
RUN pip install jupyterhub==1.1.0
RUN pip install jupyterlab notebook==6.0.3
RUN pip install jupyterlab==2.1.5
RUN pip install requests==2.31.0

# Setup Jupyter Notebook
RUN useradd -ms /bin/bash jupyter
USER jupyter
WORKDIR notebooks
EXPOSE 8888

# Define the command to run when the container starts
CMD ["jupyter", "notebook", "--allow-root", "--ip=0.0.0.0", "--port=8888"]

RUN docker run -p 8888:8888 -v ./notebooks:/notebooks my-miniconda-image

