#!/bin/bash -l

# The name of your job; be descriptive
#SBATCH --job-name=enrich_sample

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

source /shared/rc/proteome/protpen/protpen_venv/bin/activate
export PYTHONPATH="/shared/rc/proteome/protpen/ProtPen:$PYTHONPATH"

# Define input and output files
INPUT_TSV="consolidated_foldseek_results.tsv"
OUTPUT_TSV="enriched_foldseek_results.tsv"

# Ensure logs directory exists
mkdir -p logs

# Run enrichment
python -m protpen.cli_enrich \
  -i "$INPUT_TSV" \
  -o "$OUTPUT_TSV"