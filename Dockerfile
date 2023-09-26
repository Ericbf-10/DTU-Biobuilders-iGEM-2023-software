# Use a base image as a starting point
FROM ubuntu:23.04

# Install Miniconda
RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -b -p /miniconda
ENV PATH=$PATH:/miniconda/condabin:/miniconda/bin

# Install essentials like git and brew
RUN apt-get update && apt-get install -y build-essential curl file git
RUN /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
ENV PATH="/home/linuxbrew/.linuxbrew/bin:${PATH}"

# Create AptaLoop environment
RUN conda create --name AptaLoop

# Install Jupyter Notebook for viewing code
RUN pip install jupyterlab

# Install required packages for folding sequence
RUN pip install viennarna==2.6.3

# Install AutoDock Vina for docking simulation


# Install GROMACS, AmberTools for molecular dynamics
RUN conda install -c conda-forge ambertools=23
RUN brew install gromacs

# Download code from gitlab
RUN git clone https://gitlab.igem.org/2023/software-tools/dtu-denmark.git

# Setup Jupyter Notebook
RUN useradd -ms /bin/bash jupyter
RUN chown jupyter:jupyter /dtu-denmark/notebooks
USER jupyter
WORKDIR /dtu-denmark/notebooks
EXPOSE 8888

# Run Jupyter
CMD ["jupyter", "lab", "--allow-root", "--ip=0.0.0.0", "--port=8888"]
