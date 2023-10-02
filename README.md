# Team DTU-Denmark 2023 Software Tool: AptaLoop

## Description
This repository contains code for aptamer design _in silico_ developed by the **DTU Biobuilders 2023** iGEM team. The AptaLoop pipeline consists of 4 different modules, where the first 2 are mutually exclusive and the rest are meant to be used sequentially: 
1. Secondary/tertiary structure prediction
1. Making Aptamers Without Selex (MAWS)
1. Docking
1. Molecular Dynamics

We decided to use a **Jupyter Notebook** format to make sure that our code is well documented and easy to use for external people, and we encapsulated the pipeline in a docker container to ensure reproducibility. The global structure of the directory is as follows (some files have been skipped for the sake of comprehension):

```
dtu-denmark
├── data
├── heidelberg_maws
│   └── MAWS2023.py
├── notebooks
│   ├── 1_sequence_3d
│   │   ├── 1_create_sequence_file.ipynb
│   │   └── 2_aptamer_folding_3dDNA.ipynb
│   ├── 2_maws
│   │   └── maws.ipynb
│   ├── 3_docking
│   │   └── docking.ipynb
│   └── 4_molecular_dynamics
│       └── molecular_dynamics.ipynb
├── Dockerfile
├── LICENSE
├── README.md
└── requirements.txt
```

The global aim of this pipeline is to provide the necessary tools to design DNA or RNA aptamers to target a specific molecule (protein, organic or lipid), predict the secondary and tertiary structure, predict the interaction position between them (docking) and simulate the molecular dynamics. The results of these analyses can be useful to guide the wet lab efforts in finding the **best possible aptamer sequence** for the desired target molecule.
### Secondary/tertiary structure prediction
The first module is meant for those users that already have an aptamer sequence for their target molecule and want to evaluate it using our software. It consists of 2 parts:
1. The first notebook will generate a PDB file from a DNA or RNA aptamer sequence.
1. The second notebook will predict the secondary and tertiary structures of the provided aptamer sequence.
### Making Aptamers Without Selex (MAWS)
The second module is meant for those users that wish to create an aptamer from scratch to find the best possible sequence for their target molecule. It is possible to define the type of aptamer (DNA or RNA), the type of ligand molecule (protein, organic or lipid), the number of nucleotides that the aptamer should have, and others (see the notebook).
### Docking
The third module takes care of predicting the interaction location of the aptamer-molecule complex, and providing an insight of the predicted binding affinity. The results are multiple poses ranked by their predicted binding energy, where the lowest energy pose is considered the most favorable binding mode.
### Molecular Dynamics
The fourth and last module simulates the molecular dynamics of the interaction between the aptamer and the ligand molecule, which concludes our pipeline by giving an insight on the binding between the two.

## Installation
The easiest way to install the required dependencies is through Docker. Docker is a platform for developing, shipping, and running applications inside containers. It enables consistent deployment across different systems, simplifying application management and ensuring compatibility. 

So first, you need to install Docker Desktop from the official Docker website: [Docker Desktop](https://www.docker.com/products/docker-desktop). Select the version depending on your Operating System and follow the instructions to complete the installation.
### Verification
To verify that Docker is installed and running, open a terminal or command prompt and run the following command: ```docker --version```

If the output you get is ```Docker version X.Y.Z``` (where X, Y and Z are numbers), then it means you successfully installed Docker and you are ready to install the ```dtu-biobuilders-aptaloop``` image that will enable you to run our pipeline. 

Follow these steps in the terminal:
1. Pull the docker image:
```docker pull teheavy/dtu-biobuilders-aptaloop:test_new```

1. Then check if you pulled the image correctly:
```docker images```

1. If you see **teheavy/dtu-biobuilders-aptaloop:test_new**, it means everything went well. Finally, do the following to run the container:
```sudo docker run -it -p 8888:8888 teheavy/dtu-biobuilders-aptaloop:test_new```

## Usage
There are 2 possibilities of using the AptaLoop pipeline:
### 1. Already having an aptamer sequence
If the user already has an aptamer sequence, the modules to run are 1, 3 and 4.
#### Module 1: 1_sequence_3d
1. Run the NB **1_create_sequence_file.ipynb** to create a sequence PDB file.
- Input: DNA or RNA string.
- Output: PDB file.
2. Then run the NB: **2_aptamer_folding_3dDNA.ipynb** to get the secondary and tertiary structure predictions for the given aptamer sequence.
- Input: FASTA file of aptamer sequence(s).
- Output: FASTA file of secondary structure prediction(s) and tertiary structure prediction(s).
#### Module 3: 3_docking
Run the NB **docking.ipynb** to perform a docking simulation between your aptamer and ligand molecule.
- Input: 
1. PDB file for the aptamer.
1. SDF or PDB file for the ligand.
- Output: PDBQT file.
#### Module 4: 4_molecular_dynamics
Run the NB **molecular_dynamics.ipynb** to perform a molecular dynamics simulation of the aptamer-molecule complex.
- Input: 
1. PDB file containing the aptamer-molecule complex.
1. GROMACS parameter and configuration files (ions.mdp, minim.mdp, nvt.mdp, npt.mdp, md.mdp).
- Output: 
1. Processed and solvated molecular structures in GROMACS formats.
1. Energy, temperature, pressure, and density profiles during the simulation.
1. Trajectory and analysis files including RMSD, gyration, and more.
### 2. Not having an aptamer sequence
If the user does not have an aptamer sequence yet, the modules to run are 2, 3 and 4.
#### Module 2: 2_maws
Run the NB **maws.ipynb** to generate the DNA or RNA aptamer that best binds your target molecule.
- Input: PDB file of target molecule.
- Output: PDB file of aptamer + target molecule.
#### Module 3: 3_docking
Run the NB **docking.ipynb** to perform a docking simulation between your aptamer and ligand molecule.
- Input: 
1. PDB file for the aptamer.
1. SDF or PDB file for the ligand.
- Output: PDBQT file.
#### Module 4: 4_molecular_dynamics
Run the NB **molecular_dynamics.ipynb** to perform a molecular dynamics simulation of the aptamer-molecule complex.
- Input: 
1. PDB file containing the aptamer-molecule complex.
1. GROMACS parameter and configuration files (ions.mdp, minim.mdp, nvt.mdp, npt.mdp, md.mdp).
- Output: 
1. Processed and solvated molecular structures in GROMACS formats.
1. Energy, temperature, pressure, and density profiles during the simulation.
1. Trajectory and analysis files including RMSD, gyration, and more.

## Contributing
We are open to contributions, as long as our work is attributed properly.

## Authors and acknowledgment
- We want to acknowledge the authors of the original version of MAWS, the Heidelberg 2015 iGEM team: [Wiki](https://2015.igem.org/Team:Heidelberg/software/maws) and [GitHub](https://github.com/igemsoftware/Heidelberg_15/blob/master/MAWS.py). 
- We also want to thank the Heidelberg 2017 iGEM team, for making the first improvements to the MAWS software: [Wiki](https://2017.igem.org/Team:Heidelberg/Software/MAWS) and [GitHub](https://github.com/igemsoftware2017/AiGEM_TeamHeidelberg2017/tree/master/sharksome-suite). 
- Finally, we would like to thank the NU Kazakhstan 2022 iGEM team for making further improvements to the code and developing a guide on how to use MAWS: [Wiki](https://2022.igem.wiki/nu-kazakhstan/), [GitHub](https://github.com/iGEM-NU-Kazakhstan/MAWS-Heidelberg-x-NU_Kazakhstan) and [Guide](https://docs.google.com/document/d/1VpqD0gc2ZrxZVhDIr6PMhXtEJ7jFILcskNtPZiLjlmw/edit). 
## References
Abraham, M.J., Murtola, T., Schulz, R., Páll, S., Smith, J.C., Hess, B., and Lindahl, E. “GROMACS: High performance molecular simulations through multi-level parallelism from laptops to supercomputers,” SoftwareX, 1–2 19–25 (2015).

Eberhardt, J., Santos-Martins, D., Tillack, A.F., Forli, S. (2021). AutoDock Vina 1.2.0: New Docking Methods, Expanded Force Field, and Python Bindings. Journal of Chemical Information and Modeling.

Merkel, D. (2014). Docker: lightweight linux containers for consistent development and deployment. Linux Journal, 2014(239), 2.

Salomon-Ferrer, R., Case, D.A., Walker, R.C. (2013) "An overview of the Amber biomolecular simulation package." WIREs Comput. Mol. Sci. 3, 198-210.

Trott, O., & Olson, A. J. (2010). AutoDock Vina: improving the speed and accuracy of docking with a new scoring function, efficient optimization, and multithreading. Journal of computational chemistry, 31(2), 455-461.