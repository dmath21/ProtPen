#!/usr/bin/env python3
# protpen/enrich_tsvs.py
import csv
import requests
import time
import argparse
import os
import json

# Functions for downloading UniProt JSON and retrieving information

def download_uniprot_json(uniprot_id, output_file):
    """
    Downloads the UniProt JSON data for a given UniProt ID and writes it to output_file.
    """
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.json"
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_file, "w") as file_object:
            json.dump(response.json(), file_object, sort_keys=True, indent=2)
        print(f"Downloaded UniProt JSON for {uniprot_id}")
    else:
        print(f"Failed to download UniProt JSON for {uniprot_id}")

def get_uniprot_info(uniprot_id, json_dir="uniprot_json_enrich"):
    """
    Retrieves UniProt information for a given UniProt ID.
    Downloads the JSON if not already available and extracts:
      - 'description': protein name (recommended or submission name)
      - 'interpro': INTERPRO domain annotations (joined by comma if more than one)
      - 'supfam': SUPFAM annotations (joined by comma if more than one)
    
    If no data is found for a field, "n/a" is returned.
    
    Args:
        uniprot_id (str): UniProt ID.
        json_dir (str): Directory where JSON files are saved.
    
    Returns:
        dict: Dictionary with keys "description", "interpro", and "supfam".
    """
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)
    output_file = os.path.join(json_dir, f"{uniprot_id}.json")
    if not os.path.exists(output_file):
        download_uniprot_json(uniprot_id, output_file)
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            data = json.load(f)
    else:
        print(f"Unable to retrieve JSON for {uniprot_id}")
        return {"description": "n/a", "interpro": "n/a", "supfam": "n/a"}
    
    info = {"description": "", "interpro": [], "supfam": []}
    # Extract protein description: try recommendedName, then submissionNames.
    try:
        info["description"] = data["proteinDescription"]["recommendedName"]["fullName"]["value"]
    except KeyError:
        try:
            submission_names = data["proteinDescription"].get("submissionNames", [])
            if submission_names:
                info["description"] = submission_names[0]["fullName"]["value"]
        except (KeyError, IndexError):
            info["description"] = ""
    if not info["description"]:
        info["description"] = "n/a"
    
    # Process cross-references for INTERPRO and SUPFAM.
    for ref in data.get("uniProtKBCrossReferences", []):
        db = ref.get("database", "").upper()
        entry_name = ""
        for prop in ref.get("properties", []):
            if prop.get("key") == "EntryName":
                entry_name = prop.get("value")
                break
        if not entry_name:
            entry_name = ref.get("id", "")
        
        if db == "INTERPRO":
            info["interpro"].append(entry_name)
        elif db == "SUPFAM":
            info["supfam"].append(entry_name)
    
    # Join multiple annotations with a comma, or set to "n/a" if empty.
    info["interpro"] = ", ".join(info["interpro"]) if info["interpro"] else "n/a"
    info["supfam"] = ", ".join(info["supfam"]) if info["supfam"] else "n/a"
    
    return info

# Functions for UniProt mapping job
def submit_id_mapping(pdb_ids):
    """
    Submit a UniProt ID mapping job from PDB to UniProtKB for the list of pdb_ids.
    """
    url = "https://rest.uniprot.org/idmapping/run"
    params = {
        "from": "PDB",
        "to": "UniProtKB",
        "ids": ",".join(pdb_ids)
    }
    response = requests.post(url, data=params)
    if response.status_code != 200:
        print("Error submitting ID mapping:", response.text)
        return None
    job_id = response.json().get("jobId")
    return job_id

def poll_job(job_id):
    """
    Poll the mapping job until its status is FINISHED.
    """
    status_url = f"https://rest.uniprot.org/idmapping/status/{job_id}"
    while True:
        response = requests.get(status_url)
        if response.status_code != 200:
            print("Error polling job:", response.text)
            return False
        status_data = response.json()
        job_status = status_data.get("jobStatus")
        if job_status == "FINISHED" or ("results" in status_data):
            return True
        elif job_status in ("RUNNING", "NEW"):
            time.sleep(3)
        else:
            print("Job failed or returned unexpected status:", status_data)
            return False

def get_mapping_results(job_id):
    """
    Retrieve all results from a finished mapping job.
    """
    results = []
    base_url = f"https://rest.uniprot.org/idmapping/results/{job_id}"
    params = {"size": 500}
    cursor = None

    while True:
        if cursor:
            params["cursor"] = cursor
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            print("Error retrieving mapping results:", response.text)
            break
        data = response.json()
        results.extend(data.get("results", []))
        cursor = data.get("nextCursor")
        if not cursor:
            break
    return results


# TSV file processing functions
def extract_pdb_ids(target_str):
    """
    Given a target string of the format:
      "4is4-assembly1.cif.gz_H||4mdz-assembly1.cif.gz_A||..."
    return a list of PDB IDs (e.g., ["4is4", "4mdz", ...]).
    """
    pdb_ids = []
    for token in target_str.split("||"):
        if token:
            pdb_id = token.split("-")[0]
            pdb_ids.append(pdb_id)
    return pdb_ids

def enrich_tsv(input_tsv, output_tsv, pdb_to_info):
    """
    Reads the input TSV (with Foldseek results in the 'target' column) and writes
    an output TSV that includes additional columns with UniProt enrichment data.
    The new columns (prefixed with 'UniProt_') are:
      - UniProt_Description
      - UniProt_InterPro
      - UniProt_SUPFAM
    For each row the script processes the Foldseek 'target' column (separated by "||").
    For each PDB ID:
      - The UniProt information is provided.
      - If there are multiple UniProt mappings for a single PDB, their values are separated by a comma.
      - If no UniProt result is found, "n/a" is inserted.
    """
    with open(input_tsv, newline="") as infile, open(output_tsv, "w", newline="") as outfile:
        reader = csv.DictReader(infile, delimiter="\t")
        new_fields = ["UniProt_Description", "UniProt_InterPro", "UniProt_SUPFAM"]
        fieldnames = reader.fieldnames + new_fields
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for row in reader:
            target_field = row.get("target", "")
            descs = []
            interpros = []
            supfams = []
            # Process each Foldseek result (each token corresponds to a PDB ID)
            for token in target_field.split("||"):
                if token:
                    pdb_id = token.split("-")[0]
                    info = pdb_to_info.get(pdb_id, {"description": "n/a", "interpro": "n/a", "supfam": "n/a"})
                    descs.append(info.get("description", "n/a"))
                    interpros.append(info.get("interpro", "n/a"))
                    supfams.append(info.get("supfam", "n/a"))
            row["UniProt_Description"] = "||".join(descs)
            row["UniProt_InterPro"] = "||".join(interpros)
            row["UniProt_SUPFAM"] = "||".join(supfams)
            writer.writerow(row)

def main():
    parser = argparse.ArgumentParser(
        description="Enrich Foldseek TSV results with UniProt descriptions and domain annotations (InterPro, SUPFAM)."
    )
    parser.add_argument(
        "-i", "--input", required=False, help="Path to the consolidated input TSV file (Foldseek results)"
    )
    parser.add_argument(
        "-o", "--output", required=False, help="Path to write the enriched output TSV file (UniProt enrichment)"
    )
    args = parser.parse_args()

    # Step 1: Collect unique PDB IDs from the Foldseek input TSV.
    unique_pdb_ids = set()
    with open(args.input, newline="") as infile:
        reader = csv.DictReader(infile, delimiter="\t")
        for row in reader:
            target_field = row.get("target", "")
            for pdb_id in extract_pdb_ids(target_field):
                unique_pdb_ids.add(pdb_id)
    unique_pdb_ids = list(unique_pdb_ids)
    print(f"Found {len(unique_pdb_ids)} unique PDB IDs in Foldseek results.")

    if not unique_pdb_ids:
        print("No PDB IDs found in the target column. Exiting.")
        return

    # Step 2: Submit the UniProt mapping job.
    print("Submitting UniProt mapping job...")
    job_id = submit_id_mapping(unique_pdb_ids)
    if not job_id:
        print("Error: Could not submit mapping job.")
        return
    print("Job ID:", job_id)

    # Step 3: Poll until the job finishes.
    print("Waiting for mapping job to finish...")
    if not poll_job(job_id):
        print("Mapping job did not finish successfully.")
        return

    # Step 4: Retrieve mapping results.
    mapping_results = get_mapping_results(job_id)
    print(f"Retrieved {len(mapping_results)} mapping results.")

    # Build a dictionary mapping each PDB ID to a list of UniProt IDs.
    pdb_to_uniprot = {}
    for entry in mapping_results:
        pdb = entry.get("from")
        uniprot = entry.get("to")
        if pdb and uniprot:
            pdb_to_uniprot.setdefault(pdb, []).append(uniprot)

    # Step 5: For each unique PDB ID, retrieve UniProt information.
    # Cache UniProt info so that each UniProt ID is processed only once.
    uniprot_info_cache = {}
    pdb_to_info = {}
    for pdb_id, uniprot_ids in pdb_to_uniprot.items():
        desc_list = []
        interpro_list = []
        supfam_list = []
        for uid in uniprot_ids:
            if uid not in uniprot_info_cache:
                uniprot_info_cache[uid] = get_uniprot_info(uid)
            info = uniprot_info_cache[uid]
            desc_list.append(info["description"])
            interpro_list.append(info["interpro"])
            supfam_list.append(info["supfam"])
        pdb_to_info[pdb_id] = {
            # For a single PDB, multiple UniProt results are separated by a comma.
            "description": ", ".join(desc_list) if desc_list else "n/a",
            "interpro": ", ".join(interpro_list) if interpro_list else "n/a",
            "supfam": ", ".join(supfam_list) if supfam_list else "n/a"
        }

    # For any PDB IDs that did not get a mapping, mark as "n/a".
    for pdb_id in unique_pdb_ids:
        if pdb_id not in pdb_to_info:
            pdb_to_info[pdb_id] = {"description": "n/a", "interpro": "n/a", "supfam": "n/a"}

    # Step 6: Write out the enriched TSV file.
    print("Writing enriched TSV to", args.output)
    enrich_tsv(args.input, args.output, pdb_to_info)
    print("Enrichment complete.")

if __name__ == "__main__":
    main()
