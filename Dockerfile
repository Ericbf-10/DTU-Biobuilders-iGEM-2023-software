# Use a base image as a starting point
FROM ubuntu:23.04

# Install Miniconda
RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -b -p /miniconda
ENV PATH=$PATH:/miniconda/condabin:/miniconda/bin

# Create AptaLoop environment
RUN conda create --name AptaLoop

# Install Jupyter Notebook for viewing code
RUN pip install jupyterhub jupyterlab notebook jupyter-lsp

# Install required packages for folding sequence
RUN pip install viennarna==2.6.3 rna==0.11.0 requests==2.31.0

# Install AutoDock Vina for docking simulation
RUN apt-get update && apt-get install -y autodock-vina

# Install OpenBabel for chemical file format conversion
RUN apt-get install -y openbabel

# Install GROMACS, AmberTools for molecular dynamics
RUN /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
RUN brew install GROMACS

RUN conda install -c conda-forge ambertools=23
RUN conda update -c conda-forge ambertools

# Download code from gitlab
RUN git clone https://gitlab.igem.org/2023/software-tools/dtu-denmark.git

# Setup Jupyter Notebook
RUN useradd -ms /bin/bash jupyter
RUN mkdir /notebooks && chown jupyter:jupyter /notebooks
USER jupyter
WORKDIR notebooks
EXPOSE 8888

# Run Jupyter
CMD ["jupyter", "notebook", "--allow-root", "--ip=0.0.0.0", "--port=8888"]
