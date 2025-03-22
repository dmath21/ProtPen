import requests
import os
import json
import re


def main(file_in=None, output_folder="pdb_files"):
    """
    Downloads PDB files for proteins in UniProt based on a FASTA file.

    Keyword arguments:
        file_in: .fasta file containing all proteins named by UniProt IDs
        output_folder: Folder to save the PDB files (default: "pdb_files")
    """
    if file_in is None:
        print("Error: Please provide a FASTA file as input.")
        return

    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Extract protein IDs
    protein_ids = extract_protein_ids_from_fasta(file_in)
    if not protein_ids:
        print("No protein IDs found in the FASTA file.")
        return

    # Process each protein ID
    for protein_id in protein_ids:
        json_file = os.path.join(output_folder, f"{protein_id}.json")

        if not os.path.exists(json_file):
            download_uniprot_json(protein_id, json_file)

        # Load the UniProt JSON file
        with open(json_file, "r") as file_object:
            j_content = json.load(file_object)

        # Extract the AlphaFold ID and download the PDB
        alphafold_id = extract_alphafold_id(j_content)
        if alphafold_id:
            download_alphafold_pdb(alphafold_id, output_folder)
        else:
            print(f"No AlphaFold ID found for {protein_id}.")


def extract_protein_ids_from_fasta(file_in):
    """
    Extracts protein identifiers from a FASTA file, handling both UniProt-style and simple FASTA headers.

    Args:
        file_in (str): Path to the FASTA file

    Returns:
        list: List of extracted protein identifiers
    """
    protein_ids = set()
    with open(file_in, "r") as fasta_file:
        for line in fasta_file:
            if line.startswith(">"):
                # Case 1: UniProt-style header (>sp|G3XCV0|FLEQ_PSEAE ...)
                parts = line.strip().split("|")
                if len(parts) > 2:
                    protein_id = parts[1]  # Extract second field (UniProt ID)
                else:
                    # Case 2: Other formats (>PA0033 ref|NP_248723.1|gi|...)
                    match = re.match(r"^>(\S+)", line)
                    protein_id = match.group(1) if match else None
                
                if protein_id:
                    protein_ids.add(protein_id)
    
    return list(protein_ids)


def download_uniprot_json(uniprot_id, output_file):
    """
    Downloads the UniProt JSON data for a given UniProt ID.

    Args:
        uniprot_id (str): UniProt ID
        output_file (str): Path to save the JSON file
    """
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}"
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_file, "w") as file_object:
            json.dump(response.json(), file_object, sort_keys=True, indent=2)
        print(f"Downloaded UniProt JSON for {uniprot_id}")
    else:
        print(f"Failed to download UniProt JSON for {uniprot_id}")


def extract_alphafold_id(data):
    """
    Extracts the AlphaFold ID from the UniProt JSON data.

    Args:
        data (dict): UniProt JSON data

    Returns:
        str: AlphaFold ID if found, otherwise an empty string
    """
    for ref in data.get('uniProtKBCrossReferences', []):
        if ref.get('database') == 'AlphaFoldDB':
            return ref.get('id', '')
    return ''


def download_alphafold_pdb(alphafold_id, output_folder):
    """
    Downloads the AlphaFold PDB file.

    Args:
        alphafold_id (str): AlphaFold ID
        output_folder (str): Folder to save the PDB files

    Returns:
        str: Path to the downloaded PDB file if successful, otherwise None
    """
    pdb_file = f"{alphafold_id}.pdb"
    pdb_path = os.path.join(output_folder, pdb_file)
    base_url = f"https://alphafold.ebi.ac.uk/files/AF-{alphafold_id}-F1-model_v"
    version = 1

    while version <= 100:
        url = base_url + str(version) + ".pdb"
        response = requests.head(url)

        if response.status_code == 200:
            response = requests.get(url)
            with open(pdb_path, 'wb') as file:
                file.write(response.content)
            print(f"Successfully downloaded AlphaFold PDB: {pdb_file}")
            return pdb_path
        version += 1

    print(f"Failed to download AlphaFold PDB for {alphafold_id}.")
    return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Download AlphaFold PDB files from UniProt FASTA.")
    parser.add_argument("file_in", help="Input FASTA file with UniProt IDs")
    parser.add_argument("--output_folder", default="pdb_files", help="Folder to save PDB files")
    args = parser.parse_args()

    main(file_in=args.file_in, output_folder=args.output_folder)
