# protpen/cli_eggnog.py
import argparse
from protpen.eggnog import run_eggnog_mapper, convert_to_tsv

def main():
    parser = argparse.ArgumentParser(description="Run EggNOG-mapper and convert output to TSV")
    parser.add_argument("-i", "--input_fasta", default="input_proteins.fasta", help="Input FASTA file")
    parser.add_argument("-o", "--output_dir", default="eggnog_output", help="Output directory")
    parser.add_argument("-p", "--output_prefix", default="test_proteins", help="Output prefix")
    parser.add_argument("-t", "--output_tsv", default="eggnog_output.tsv", help="Output TSV path")

    args = parser.parse_args()
    run_eggnog_mapper(args.input_fasta, args.output_dir, args.output_prefix)
    convert_to_tsv(args.output_dir, args.output_prefix, args.output_tsv)

if __name__ == "__main__":
    main()
