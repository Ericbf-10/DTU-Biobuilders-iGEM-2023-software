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
RUN git clone https://github.com/Ericbf-10/DTU-Biobuilders-iGEM-2023-software

# Create AptaLoop environment and activate
RUN conda env create --file dtu-denmark/environment.yml

# Install AutoDock Vina for docking simulation
RUN apt-get update && apt-get install -y autodock-vina

# Install OpenBabel for chemical file format conversion
RUN apt-get install -y openbabel

# Install dependencies for building GROMACS
RUN apt-get update && apt-get install -y build-essential cmake curl

# Download GROMACS source code
RUN curl -O https://ftp.gromacs.org/pub/gromacs/gromacs-2021.4.tar.gz

# Unpack GROMACS source code
RUN tar -xf gromacs-2021.4.tar.gz

# Create build directory and move into it
RUN mkdir /gromacs-2021.4/build
WORKDIR /gromacs-2021.4/build

# Configure and build GROMACS without rdtscp, afterwards cleanup
RUN cmake .. -DGMX_BUILD_OWN_FFTW=ON -DGMX_USE_RDTSCP=OFF \
    && make \
    && make install \
    && rm ../../gromacs-2021.4.tar.gz \
    && rm -rf ../../gromacs-2021.4

# Create symbolic link to GROMACS binaries
RUN ln -s /usr/local/gromacs/bin/gmx /usr/bin/gmx

# Setup Jupyter Notebook
WORKDIR /dtu-denmark
RUN useradd -ms /bin/bash jupyter
RUN chown -R jupyter:jupyter /miniconda/envs/AptaLoop
RUN chown -R jupyter:jupyter /dtu-denmark
RUN chmod -R 777 /dtu-denmark
USER jupyter
RUN /bin/bash -c "source /miniconda/bin/activate AptaLoop && python -m ipykernel install --user --name AptaLoop --display-name 'Python (AptaLoop)'"
WORKDIR /dtu-denmark
EXPOSE 8888

# Run Jupyter
CMD ["/bin/bash", "-c", "source /miniconda/bin/activate AptaLoop && jupyter lab --allow-root --ip=0.0.0.0 --port=8888"]
