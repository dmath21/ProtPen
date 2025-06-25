import os
import subprocess

def run_foldseek_search(pdb_dir, output_dir, tmp_dir="tmp"):
    """
    Runs Foldseek searches for all PDB files in a directory.

    Args:
        pdb_dir (str): Directory containing PDB files.
        output_dir (str): Directory to save Foldseek output TSV files.
        tmp_dir (str): Temporary directory for Foldseek. Defaults to "tmp".
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    pdb_files = [f for f in os.listdir(pdb_dir) if f.endswith(".pdb")]

    if not pdb_files:
        print("No PDB files found in the specified directory.")
        return

    for pdb_file in pdb_files:
        pdb_path = os.path.join(pdb_dir, pdb_file)
        output_file = os.path.join(output_dir, f"{os.path.splitext(pdb_file)[0]}.tsv")
        # specify the protein database to search against
        command = [
            "foldseek", 
            "easy-search", 
            pdb_path, 
            "pdb", 
            #"afdb",
            output_file, 
            tmp_dir, 
            "--format-mode", "4" #change the format mode if needed
        ]

        print(f"Running Foldseek for {pdb_file}...")
        try:
            subprocess.run(command, check=True)
            print(f"Results saved to {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error running Foldseek for {pdb_file}: {e}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run Foldseek search on PDB files in a directory.")
    parser.add_argument("pdb_dir", help="Directory containing PDB files.")
    parser.add_argument("output_dir", help="Directory to save output TSV files.")
    parser.add_argument("--tmp_dir", default="tmp", help="Temporary directory for Foldseek. Defaults to 'tmp'.")
    args = parser.parse_args()

    run_foldseek_search(args.pdb_dir, args.output_dir, args.tmp_dir)
