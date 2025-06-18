# ProtPen: Protein Function Prediction Pipeline

This repository contains a pipeline for predicting and analyzing protein function using structure- and sequence-based methods. The pipeline integrates EggNOG-mapper, AlphaFold structure retrieval, Foldseek searches, and result enrichment to investigate differentially abundant proteins of unknown function in a proteomic dataset. 

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Pipeline Workflow](#pipeline-workflow)
- [Scripts](#scripts)
- [Usage](#usage)
- [Output](#output)

## Overview
ProtPen takes a FASTA file containing UniProt protein identifiers as input, retrieves AlphaFold PDB structures, performs eggNOG-mapper and Foldseek searches, and consolidates results to facilitate functional annotation.

## Installation
This pipeline requires Python and various dependencies. It is designed to run on an HPC system with SLURM.

### Prerequisites
Ensure the following dependencies are installed:
- Python 3.x
- EggNOG-mapper v2
- Foldseek
- psutil v6.0+
- Required Python libraries: `pandas`, `requests`, `biopython`, `pytest`

### Clone the Repository
```sh
 git clone https://github.com/dmath21/ProtPen.git
```

## Pipeline Workflow
1. **Run EggNOG-mapper** to annotate proteins with functional information.
2. **Download AlphaFold PDB files** from UniProt.
3. **Run Foldseek** to compare structures against a reference database.
4. **Filter and consolidate Foldseek results** based on query proteins.
5. **Enrich results** by mapping PDB IDs to UniProt IDs and retrieving additional protein metadata.
6. **Merge results** from EggNOG-mapper and Foldseek.

## Scripts
The pipeline consists of the following scripts:

1. `run_eggnog_mapper.py`: Runs EggNOG-mapper on a FASTA file with UniProt IDs, generating TSV output.
2. `download_AF_from_uniprot.py`: Downloads AlphaFold PDB files for proteins in the FASTA file.
3. `foldseek_command_line_search.py`: Runs Foldseek searches on the PDB files.
4. `filter_sort_consolidate_foldseek_results.py`: Filters Foldseek results and consolidates them into a single TSV file.
5. `enrich_tsvs.py`: Maps PDB IDs to UniProt IDs and appends additional protein metadata.
6. `merge_tsvs.py`: Merges results from EggNOG-mapper and Foldseek into a unified TSV file.

## Usage
### Running the Pipeline
Example workflow for running ProtPen:
```sh
python run_eggnog_mapper.py -i input.fasta -o output_dir/
python download_AF_from_uniprot.py -i input.fasta -o af_pdbs/
python foldseek_command_line_search.py -q af_pdbs/ -t target_db/ -o foldseek_results/
python filter_sort_consolidate_foldseek_results.py -q input.fasta -i foldseek_results/ -o consolidated.tsv
python enrich_tsvs.py -i consolidated.tsv -o enriched.tsv
python merge_tsvs.py -e enriched.tsv -g eggnog_output.tsv -o final_results.tsv
```

## Output
- `final_results.tsv`: Consolidated results integrating sequence and structure-based annotations.
- Intermediate TSV files with Foldseek and EggNOG-mapper results.
- AlphaFold PDB files for query proteins.
