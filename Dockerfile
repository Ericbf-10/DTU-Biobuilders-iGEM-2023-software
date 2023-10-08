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

# Download code from gitlab
RUN git clone https://gitlab.igem.org/2023/software-tools/dtu-denmark.git

# Create AptaLoop environment and activate
RUN conda env create --file dtu-denmark/environment.yml

# Install AutoDock Vina for docking simulation
RUN apt-get update && apt-get install -y autodock-vina

# Install OpenBabel for chemical file format conversion
RUN apt-get install -y openbabel

# Install GROMACS for molecular dynamics
RUN brew install gromacs

# Setup Jupyter Notebook
RUN useradd -ms /bin/bash jupyter
RUN chown -R jupyter:jupyter /miniconda/envs/AptaLoop
RUN chown -R jupyter:jupyter /dtu-denmark/notebooks
RUN chmod 777 /dtu-denmark/notebooks
USER jupyter
RUN /bin/bash -c "source /miniconda/bin/activate AptaLoop && python -m ipykernel install --user --name AptaLoop --display-name 'Python (AptaLoop)'"
WORKDIR /dtu-denmark
EXPOSE 8888

# Run Jupyter
CMD ["/bin/bash", "-c", "source /miniconda/bin/activate AptaLoop && jupyter lab --allow-root --ip=0.0.0.0 --port=8888"]
