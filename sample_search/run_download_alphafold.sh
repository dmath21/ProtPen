#!/bin/bash -l

# The name of your job; be descriptive
#SBATCH --job-name=sample_download

# Where to save the output and error messages for your job?
# %x will fill in your job name, %j will fill in your job ID
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err

#SBATCH --nodes=1

# How many tasks does your job need?
#SBATCH --ntasks=1

# How much time does your job need to run?
#SBATCH --time=0-04:00:00

# How much memory per CPU: MB=m (default), GB=g, TB=t
#SBATCH --cpus-per-task=8   
#SBATCH --mem=32g

# Your slurm account
#SBATCH --account=proteome

# The partition to run your job on
#SBATCH --partition=debug

# Load necessary modules
source /shared/rc/proteome/protpen/protpen_venv/bin/activate
#spack env activate default-genomics-x86_64-24120601
export PYTHONPATH="/shared/rc/proteome/protpen/ProtPen:$PYTHONPATH"


ROOT_DIR="/shared/rc/proteome/protpen/ProtPen" # stays the same 
INPUT_FASTA="sample_proteins.fasta"       # should be in the same directory as this script and should be the input file for the pipeline
OUTPUT_PREFIX="sample_run" 
EGGNOG_DIR="eggnog_output"
EGGNOG_TSV="eggnog_results.tsv"
PDB_DIR="pdbs" #stays the same
FOLDSEEK_DIR="foldseek_output"
OUTPUT_DIR="sample_pdb"

mkdir -p "${OUTPUT_DIR}"
# Step 4: Download PDBs from UniProt
python -m protpen.cli_download \
  "${INPUT_FASTA}" \
    --output_folder "${OUTPUT_DIR}"




