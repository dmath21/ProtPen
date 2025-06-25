# Sample Protein Annotation Pipeline (`sample_search`)

This sample pipeline demonstrates how to annotate a set of protein sequences using the **ProtPen** toolkit, integrating both sequence-based (EggNOG-mapper) and structure-based (Foldseek) annotation methods. The pipeline is designed to run on an HPC cluster with SLURM workload manager.

## Directory Structure

```
sample_search/
├── sample_proteins.fasta
├── run_eggnog_mapper.sh
├── run_download_alphafold.sh
├── run_foldseek.sh
├── run_consolidate.sh
├── run_enrich.sh
├── run_merge.sh
└── logs/  # Created automatically by each script
```

## Requirements

- SLURM-based HPC environment
- Python 3.8+
- Activated ProtPen virtual environment (`protpen_venv`)
- Properly configured `$PYTHONPATH` pointing to the ProtPen codebase
- Preprocessed Foldseek database available (for `cli_foldseek`)
- Diamond module for EggNOG (`spack load diamond@2.1.7`)

## Input

- `sample_proteins.fasta`: FASTA file with UniProt protein accessions.

## Pipeline Steps

### 1. EggNOG-mapper: Functional Annotation (Sequence-based)

```bash
sbatch run_eggnog_mapper.sh
```
- Output: `sample_eggnog_output/` and `eggnog_results.tsv`

### 2. AlphaFold Structure Download

```bash
sbatch run_download_alphafold.sh
```
- Downloads AlphaFold PDB files into `sample_pdb/`

### 3. Foldseek Search: Structure-based Annotation

```bash
sbatch run_foldseek.sh
```
- Compares PDBs against a Foldseek database.
- Output: `sample_foldseek_output/`

### 4. Consolidate Foldseek Results

```bash
sbatch run_consolidate.sh
```
- Filters Foldseek results to top hits per query and retains only relevant entries.
- Output: `consolidated_foldseek_results.tsv`

### 5. Enrich Foldseek Results

```bash
sbatch run_enrich.sh
```
- Adds UniProt-based metadata to Foldseek hits.
- Output: `enriched_foldseek_results.tsv`

### 6. Merge Sequence- and Structure-based Annotations

```bash
sbatch run_merge.sh
```
- Merges EggNOG and Foldseek annotation outputs into a single file.
- Output: `merged_annotations.tsv`

## Output Summary

| File                          | Description                                      |
|------------------------------|--------------------------------------------------|
| `eggnog_results.tsv`         | Sequence-based annotations                      |
| `enriched_foldseek_results.tsv` | Structure-based annotations (with metadata)     |
| `merged_annotations.tsv`     | Final merged annotations from both approaches   |

## Notes

- Modify file names or directories in each SLURM script as needed.
- Ensure all scripts have execute permissions (`chmod +x run_*.sh`).
- Logs are automatically saved in the `logs/` directory.
