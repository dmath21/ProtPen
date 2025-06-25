import subprocess
import pandas as pd
import os
import argparse

"""
--input_fasta defaults to input_proteins.fasta.
--output_dir defaults to eggnog_output.
--output_prefix defaults to test_proteins.
--output_tsv defaults to eggnog_output.tsv.

to run: 
python run_eggnog_mapper3.py -i custom_proteins.fasta -o custom_output_dir -p custom_prefix -t custom_output.tsv
"""

# Step 1: Run EggNOG-mapper
def run_eggnog_mapper(input_fasta, output_dir, output_prefix):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Command to run EggNOG-mapper. Change the path based on where you have it installed
    # Uses both diamond and mmseqs2 for the search. 
    command = f"/shared/rc/proteome/BASIL/eggnog-mapper/emapper.py -i {input_fasta} -m diamond -m mmseqs -o {os.path.join(output_dir, output_prefix)} --excel"
    subprocess.run(command, shell=True, check=True, env=os.environ)

# Step 2: Convert output to TSV
def convert_to_tsv(output_dir, output_prefix, output_file):
    annotation_file = os.path.join(output_dir, output_prefix + ".emapper.annotations")
    data = []
    with open(annotation_file, "r") as f:
        for line in f:
            if not line.startswith("#"):
                data.append(line.strip().split("\t"))
    
    columns = [
        "query", "seed_ortholog", "evalue", "score", "eggNOG_OGs", "max_annot_lvl",
        "COG_category", "Description", "Preferred_name", "GOs", "EC", "KEGG_ko",
        "KEGG_Pathway", "KEGG_Module", "KEGG_Reaction", "KEGG_rclass", "BRITE",
        "KEGG_TC", "CAZy", "BiGG_Reaction", "PFAMs"
    ]
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(output_file, index=False, sep="\t")

# Main function
def main():
    parser = argparse.ArgumentParser(description="Run EggNOG-mapper and convert output to TSV")
    parser.add_argument("-i", "--input_fasta", default="input_proteins.fasta", help="Path to input FASTA file")
    parser.add_argument("-o", "--output_dir", default="eggnog_output", help="Directory to store EggNOG-mapper output")
    parser.add_argument("-p", "--output_prefix", default="test_proteins", help="Prefix for EggNOG-mapper output files")
    parser.add_argument("-t", "--output_tsv", default="eggnog_output.tsv", help="Path to save the output TSV file")
    
    args = parser.parse_args()

    run_eggnog_mapper(args.input_fasta, args.output_dir, args.output_prefix)
    convert_to_tsv(args.output_dir, args.output_prefix, args.output_tsv)

if __name__ == "__main__":
    main()
