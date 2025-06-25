#!/bin/bash -l

# The name of your job; be descriptive
#SBATCH --job-name=merge_sample

# Where to save the output and error messages for your job?
# %x will fill in your job name, %j will fill in your job ID
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err

#SBATCH --nodes=1

# How many tasks does your job need?
#SBATCH --ntasks=1

# How much time does your job need to run?
#SBATCH --time=10:00

# How much memory per CPU: MB=m (default), GB=g, TB=t
#SBATCH --cpus-per-task=4
#SBATCH --mem=4G

# Your slurm account
#SBATCH --account=proteome

# The partition to run your job on
#SBATCH --partition=debug

source /shared/rc/proteome/protpen/protpen_venv/bin/activate
export PYTHONPATH="/shared/rc/proteome/protpen/ProtPen:$PYTHONPATH"

# Define input and output files
EGGNOG_TSV="eggnog_results.tsv"
FOLDSEEK_TSV="enriched_foldseek_results.tsv"
MERGED_TSV="merged_annotations.tsv"

# Ensure logs directory exists
mkdir -p logs

# Run merge script
python -m protpen.cli_merge \
  "$EGGNOG_TSV" \
  "$FOLDSEEK_TSV" \
  "$MERGED_TSV"
