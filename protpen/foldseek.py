#protpen/foldseek.py
import os
import subprocess

def run_foldseek_search(pdb_dir, output_dir, tmp_dir="tmp", db="pdb"):
    """
    Runs Foldseek easy-search for all .pdb files in pdb_dir.
    
    Args:
        pdb_dir (str): Input directory containing .pdb files.
        output_dir (str): Directory to write output .tsv files.
        tmp_dir (str): Temporary directory for Foldseek processing.
        db (str): Database to search against (default: "pdb").
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
        command = [
            "foldseek",
            "easy-search",
            pdb_path,
            db,
            output_file,
            tmp_dir,
            "--format-mode", "4"
        ]

        print(f"Running Foldseek for {pdb_file}...")
        try:
            subprocess.run(command, check=True)
            print(f"Results saved to {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error running Foldseek for {pdb_file}: {e}")
