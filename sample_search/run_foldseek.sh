#!/bin/bash -l

# The name of your job; be descriptive
#SBATCH --job-name=sample_foldseek_

# Where to save the output and error messages for your job?
# %x will fill in your job name, %j will fill in your job ID
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err

#SBATCH --nodes=1

# How many tasks does your job need?
#SBATCH --ntasks=1

# How much time does your job need to run?
#SBATCH --time=1:00:00

# How much memory per CPU: MB=m (default), GB=g, TB=t
#SBATCH --cpus-per-task=16
#SBATCH --mem=100G

# Your slurm account
#SBATCH --account=proteome

# The partition to run your job on
#SBATCH --partition=debug 

# Activate virtual environment (or use one consistent environment)
spack env activate default-genomics-x86_64-24120601
source /shared/rc/proteome/protpen/protpen_venv/bin/activate
export PYTHONPATH="/shared/rc/proteome/protpen/ProtPen:$PYTHONPATH"
# Define paths and parameters
QUERY_DIR="sample_pdb"
DB_DIR="/shared/rc/proteome/protpen/run_pipeline/pdb"  # Must be preprocessed with foldseek createdb
OUT_DIR="sample_foldseek_output"
TMP_DIR="sample_foldseek_tmp"

# Create output directories if they don't exist
mkdir -p "$OUT_DIR"
mkdir -p "$TMP_DIR"
mkdir -p logs

# Run Foldseek via the CLI wrapper
python -m protpen.cli_foldseek \
  "$QUERY_DIR" \
  "$OUT_DIR" \
  --db "$DB_DIR" \
  --tmp_dir "$TMP_DIR"
