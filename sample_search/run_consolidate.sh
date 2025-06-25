#!/bin/bash -l

# The name of your job; be descriptive
#SBATCH --job-name=sample_consolidate

# Where to save the output and error messages for your job?
# %x will fill in your job name, %j will fill in your job ID
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err

#SBATCH --nodes=1

# How many tasks does your job need?
#SBATCH --ntasks=1

# How much time does your job need to run?
#SBATCH --time=30:00

# How much memory per CPU: MB=m (default), GB=g, TB=t
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G

# Your slurm account
#SBATCH --account=proteome

# The partition to run your job on
#SBATCH --partition=debug

# Activate environment
source /shared/rc/proteome/protpen/protpen_venv/bin/activate
export PYTHONPATH="/shared/rc/proteome/protpen/ProtPen:$PYTHONPATH"

# Define input and output paths
INPUT_DIR="sample_foldseek_output"
OUTPUT_FILE="consolidated_foldseek_results.tsv"
QUERY_FASTA="sample_proteins.fasta"
TOP_X=5

# Ensure logs directory exists
mkdir -p logs

# Run the consolidation script using module-style call
python -m protpen.cli_consolidate_foldseek \
  "$INPUT_DIR" \
  "$OUTPUT_FILE" \
  "$QUERY_FASTA" \
  --top_x "$TOP_X"