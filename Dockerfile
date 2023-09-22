# Use a base image as a starting point
FROM ubuntu:20.04

# Install Miniconda
RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -b -p /miniconda
ENV PATH=$PATH:/miniconda/condabin:/miniconda/bin

# Create AptaLoop environment
RUN conda create --name AptaLoop
RUN conda activate AptaLoop

# Install Jupyter Notebook for viewing code
RUN pip install jupyterhub jupyterlab notebook jupyter-lsp

# Install required packages for folding sequence
RUN pip install viennarna==2.6.3
RUN pip install rna==0.11.0
RUN pip install requests==2.31.0

# Install AutoDock Vina for docking simulation
# TODO: Put new code here

# Install GROMACS, AmberTools for molecular dynamics
RUN /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
RUN brew install GROMACS

RUN conda install -c conda-forge ambertools=23
RUN conda update -c conda-forge ambertools

# Setup Jupyter Notebook
RUN useradd -ms /bin/bash jupyter
USER jupyter
WORKDIR notebooks
EXPOSE 8888

# Run Jupyter
CMD ["jupyter", "notebook", "--allow-root", "--ip=0.0.0.0", "--port=8888"]
RUN docker run -p 8888:8888 -v ./notebooks:/notebooks my-miniconda-image

