#MAWS is part of the sharksome software suite
#This software is published under MIT license
#COPYRIGHT 2017 Michael Jendrusch
#Authors: Michael Jendrusch, Stefan Holderbach

#VERSION Information
#Note: This information should be updated with every technical change to ensure that
#      every calculation can be linked to its software version.

# Modifications were made by DTU Biobuilders in 2023

VERSION = "2.0"
RELEASE_DATE = "2017"
METHOD = "Kullback-Leibler"

import copy
import numpy as np
import argparse
from datetime import datetime
from LoadFrom import XMLStructure
from helpers import nostrom
from Complex import Complex
from Structure import Structure
from Routines import ZPS, S
from Kernels import centerOfMass
from collections import defaultdict
from operator import itemgetter
from openmm import unit
from openmm import app
import Space
import os
import subprocess

#Parser
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", type=str, default="MAWS_aptamer", help="Job name.")
parser.add_argument("-nt", "--ntides", type=int, default=15, help="Number of nucleotides in the aptamer.")
parser.add_argument("-p", "--path", type=str, default="./pfoa.pdb", help="Path to your PDB file.")
parser.add_argument("-ta", "--aptamertype", type=str, default="RNA", help="Type of aptamer, can be either DNA or RNA.")
parser.add_argument("-tm", "--moleculetype", type=str, default="protein", help="Type of ligand molecule, can be either protein, organic or lipid.")
parser.add_argument("-cenv", "--condaenv", type=str, default="maws_p3", help="Name of your conda environment that contains requirements.txt")
parser.add_argument("-b", "--beta", type=float, default=0.01, help="Inverse temperature.")
parser.add_argument("-c1", "--firstchunksize", type=int, default=5000, help="Number of samples in the first MAWS step.")
parser.add_argument("-c2", "--secondchunksize", type=int, default=5000, help="Number of samples in all subsequent MAWS steps.")
args = parser.parse_args()

#PARAMS
JOB_NAME = args.name
BETA = args.beta
FIRST_CHUNK_SIZE = args.firstchunksize
SECOND_CHUNK_SIZE = args.secondchunksize
N_NTIDES = args.ntides
PDB_PATH = args.path
ATPAMER_TYPE = args.aptamertype
MOLECULE_TYPE = args.moleculetype
CONDA_ENV = args.condaenv
N_ELEMENTS = 4 # Number of rotable junctions in RNA/DNA, to distinguish forward and backward rotation

#Open a pdb file, to monitor progress
output = open("{0}_output.log".format(JOB_NAME),"w")
entropyLog = open("{0}_entropy.log".format(JOB_NAME), "w")
step = open("{0}_step_cache.pdb".format(JOB_NAME), "w")

#Starting logfile
output.write("MAWS - Making Aptamers With Software\n")
output.write("Active version: {0} (released:_{1})\n".format(VERSION, RELEASE_DATE))
output.write("Computational method: {0}\n".format(METHOD))
output.write("Type of aptamer: {0}\n".format(ATPAMER_TYPE))
output.write("Type of ligand molecule: {0}\n".format(MOLECULE_TYPE))
output.write("Job: {0}\n".format(JOB_NAME))
output.write("Input file: {0}\n".format(PDB_PATH))
output.write("Sample number in initial step: {0}\n".format(FIRST_CHUNK_SIZE))
output.write("Sample number per further steps: {0}\n".format(SECOND_CHUNK_SIZE))
output.write("Number of further steps: {0} (sequence length = {1})\n".format(N_NTIDES, N_NTIDES + 1))
output.write("Value of beta: {0}\n".format(BETA))
output.write("Start time: {0}\n".format(str(datetime.now())))

#Choose suitable force field file for aptamer
script_path = os.path.dirname(os.path.abspath(__file__))
if ATPAMER_TYPE == "RNA":
	xml_molecule = XMLStructure(os.path.join(script_path, "RNA.xml")) #Build Structure-object for RNA residues
	nt_list = "GAUC"
	force_field_aptamer = "leaprc.RNA.OL3"
elif ATPAMER_TYPE == "DNA":
	xml_molecule = XMLStructure(os.path.join(script_path, "DNA.xml")) #Build Structure-object for DNA residues
	nt_list = "GATC"
	force_field_aptamer = "leaprc.DNA.OL21"
else: # Error handling
	print("The type of aptamer was not properly set. It can only be DNA or RNA. Stopping the program.") #Option is not well defined, break program
	exit()
output.write("Force field selected for the aptamer: {0}\n".format(force_field_aptamer))

#Choose suitable force field file for ligand
if MOLECULE_TYPE == "protein":
	force_field_ligand = "leaprc.protein.ff19SB"
elif MOLECULE_TYPE == "organic":
	force_field_ligand = "leaprc.gaff2"
elif MOLECULE_TYPE == "lipid":
	force_field_ligand = "leaprc.lipid21"
else: # Error handling
	print("The type of molecule was not properly set. It can only be protein, organic or lipid. Stopping the program.") #Option is not well defined, break program
	exit()
output.write("Force field selected for the ligand molecule: {0}\n".format(force_field_ligand))

#Instantiate the Complex for further computation
cpx = Complex(force_field_aptamer=force_field_aptamer, force_field_ligand=force_field_ligand, conda_env=CONDA_ENV)

#Add an empty Chain to the Complex, of structure RNA or DNA
cpx.add_chain('', xml_molecule)

#Add a chain to the complex using a pdb file (e.g. "pfoa.pdb")
cpx.add_chain_from_PDB(pdb_path=PDB_PATH, force_field_aptamer=force_field_aptamer, force_field_ligand=force_field_ligand,parameterized=False)

#Build a complex with the pdb only, to get center of mass of the pdb --#
c = Complex(force_field_aptamer=force_field_aptamer, force_field_ligand=force_field_ligand, conda_env=CONDA_ENV)

c.add_chain_from_PDB(pdb_path=PDB_PATH, force_field_aptamer=force_field_aptamer, force_field_ligand=force_field_ligand,parameterized=False)

c.build()
#----------------------------------------------------------------------#

#Create a sampling Cube of Diameter 50. Angstroms around the pdb center of mass
cube = Space.Cube(20., centerOfMass(np.asarray(nostrom(c.positions))))

#Create a sampling Space of the direct sum of N_ELEMENTS angles
rotations = Space.NAngles(N_ELEMENTS)

#Initialize variables for picking out the best aptamer
best_entropy = None
best_sequence = None
best_positions = None

output.write("Initialized succesfully!\n")

#for each nucleotide
for ntide in nt_list:
	output.write("{0}: starting initial step for '{1}'\n".format(str(datetime.now()),ntide))
	energies = []
	free_E = None
	position = None
	#Get a full copy of our Complex
	complex = copy.deepcopy(cpx)
	#Pick a chain to be our aptamer
	aptamer = complex.chains[0]
	#Initialize the chain with a nucleotide
	aptamer.create_sequence(ntide)
	#Build the Complex
	print("INTO LEAP ---------------------------------------------------------------------")
	complex.build()
	print("OUT OF LEAP -------------------------------------------------------------------")
	#Remember its initial positions
	positions0 = complex.positions[:]
	#For the number of samples
	for i in range(FIRST_CHUNK_SIZE):
		#Get a new sample from the cube
		orientation = cube.generator()
		#Get a new sample from the angles
		rotation = rotations.generator()
		#Translate the aptamer by the displacement part of the sample from the cube generator
		aptamer.translate_global(orientation[0:3]*unit.angstrom)
		#Rotate the aptamer by the rotation part of the sample from the cube generator
		aptamer.rotate_global(orientation[3:-1]*unit.angstrom, orientation[-1])
		#For all thing rotating
		for j in range(N_ELEMENTS):
			#Rotate around the bond by generated angle
			aptamer.rotate_in_residue(0, j, rotation[j])
		#Get energy of the complex
		energy = complex.get_energy()[0]
		#Compare to lowest energy, if lowest...
		if free_E == None or energy < free_E:
			#Tell
			print(energy)
			#Set free energy to energy
			free_E = energy
			#Remember positions
			position = complex.positions[:]
		#Remember energy
		energies.append(energy)
		#Reset positions
		complex.positions = positions0[:]
	#Calculate entropy
	entropy = S(energies, beta=BETA)

	#Performing outputs
	pdblog = open("{0}_1_{1}.pdb".format(JOB_NAME,ntide),"w")
	app.PDBFile.writeModel(copy.deepcopy(complex.topology), position[:], file=pdblog, modelIndex=1)
	pdblog.close()

	entropyLog.write("SEQUENCE: {0} ENTROPY: {1} ENERGY: {2}\n".format(aptamer.alias_sequence, entropy, free_E))
	#Check if best ...
	if best_entropy == None or entropy < best_entropy:
		best_entropy = entropy
		best_sequence = ntide
		best_ntide = ntide
		best_positions = position[:]
		best_topology = copy.deepcopy(complex.topology)

app.PDBFile.writeModel(best_topology, best_positions, file=step, modelIndex=1)
#Output best as well
pdblog = open("{0}_best_1_{1}.pdb".format(JOB_NAME,best_ntide),"w")
app.PDBFile.writeModel(best_topology, best_positions, file=pdblog, modelIndex=1)
pdblog.close()

output.write("{0}: Completed first step. Selected nucleotide: {1}\n".format(str(datetime.now()), best_sequence))
output.write("{0}: Starting further steps to append {1} nucleotides\n".format(str(datetime.now()), N_NTIDES))

#For how many nucleotides we want
for i in range(1, N_NTIDES):
	#Same as above, more or less
	best_old_sequence = best_sequence
	best_old_positions = best_positions[:]
	best_entropy = None
	for ntide in nt_list:
		#For append nucleotide or prepend nucleotide
		for append in [True, False]:
			energies = []
			free_E = None
			position = None
			#Get our complex
			complex = copy.deepcopy(cpx)
			#Get our aptamer
			aptamer = complex.chains[0]
			aptamer.create_sequence(best_old_sequence)
			print("INTO LEAP ------------------------------------------------------------------------------")
			complex.build()
			print("OUT OF LEAP ----------------------------------------------------------------------------")
			#Readjust positions
			complex.positions = best_old_positions[:]
			if append:
				#Append new nucleotide
				aptamer.append_sequence(ntide)
			else:
				#Prepend new nucleotide
				aptamer.prepend_sequence(ntide)
			print("INTO LEAP ------------------------------------------------------------------------------")
			complex.rebuild()
			print("OUT OF LEAP ----------------------------------------------------------------------------")
			## Optionally minimize or "shake" complex, to find lower energy local minimum
			#not recommended! causes issues with proteins
			#complex.minimize()
			complex.pert_min(size=0.5)
			#Remember positions
			positions0 = complex.positions[:]

			#For number of samples
			for k in range(SECOND_CHUNK_SIZE):
				#Get random angles
				rotation = rotations.generator()
				#For everything forward
				for j in range(N_ELEMENTS-1):
					#Rotate the new nucleotide's bonds
					if append:
						aptamer.rotate_in_residue(-1, j, rotation[j])
					else:
						aptamer.rotate_in_residue(0, j, rotation[j], reverse=True)
				#For everything backward (C3'-O3')
				#Rotate the old nucleotides' bond
				if append:
					aptamer.rotate_in_residue(-2, 3, rotation[3])
				else:
					aptamer.rotate_in_residue(0, 3, rotation[3], reverse=True)
				#Get energy
				energy = complex.get_energy()[0]
				#Check if best
				if free_E == None or energy < free_E:
					print(energy)
					free_E = energy
					position = complex.positions[:]
				#Remember energies
				energies.append(energy)
				#Reset positions
				complex.positions = positions0[:]

			entropy = S(energies, beta=BETA)

			#outputs
			pdblog = open("{0}_{1}_{2}.pdb".format(JOB_NAME, i+1, ntide), "w")
			app.PDBFile.writeModel(copy.deepcopy(complex.topology), position[:], file=pdblog, modelIndex=1)
			pdblog.close()

			entropyLog.write("SEQUENCE: {0} ENTROPY: {1} ENERGY: {2}\n".format(aptamer.alias_sequence, entropy, free_E))
			#Choose best
			if best_entropy == None or entropy < best_entropy:
				best_entropy = entropy
				best_positions = position[:]
				best_ntide = ntide
				best_sequence = aptamer.alias_sequence
				best_topology = copy.deepcopy(complex.topology)
	app.PDBFile.writeModel(best_topology, best_positions, file=step, modelIndex=1)
	#Output best as well
	output.write("{0}: Completed step {1}. Selected sequence: {2}\n".format(str(datetime.now()), i+1, best_sequence))
	pdblog = open("{0}_best_{1}_{2}.pdb".format(JOB_NAME, i+1, best_ntide),"w")
	app.PDBFile.writeModel(best_topology, best_positions, file=pdblog, modelIndex=1)
	pdblog.close()

#Render resulting aptamer to pdb
result_complex = copy.deepcopy(cpx)
aptamer = result_complex.chains[0]
aptamer.create_sequence(best_sequence)
result_complex.build()
result_complex.positions = best_positions[:]
pdb_out_name = f"{JOB_NAME}_RESULT.pdb"
pdb_result = open(f"{pdb_out_name}","w")
app.PDBFile.writeModel(result_complex.topology, result_complex.positions, file=pdb_result)
pdb_result.close()

# Write output ready for GROMACS
pdb_out_name2 = f"{JOB_NAME}_RESULT_GROMACS.pdb"
if ATPAMER_TYPE == "RNA":
	cmd = f'''awk '{{printf "%-6s%5s %4s %-3s %1s %4s    %8.3f%8.3f%8.3f  %5.2f %5.2f           %2s\\n", $1, $2, $3, ($4 != "LIG" ? "R"$4 : $4), $5, $6, $7, $8, $9, $10, $11, $12}}' {pdb_out_name} > {pdb_out_name2}'''
elif ATPAMER_TYPE == "DNA":
	cmd = f'''cp {pdb_out_name} {pdb_out_name2}'''

# Execute the command
subprocess.run(cmd, shell=True, check=True)

output.write("{0}: Run completed. Thank you for using MAWS!\n\n".format(str(datetime.now())))
output.write("Final sequence: {0}\n".format(best_sequence))

#Garbage collection
step.close()
entropyLog.close()
output.close()
