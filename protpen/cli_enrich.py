#!/usr/bin/env python3
# protpen/cli_enrich.py

# usage: python protpen/cli_enrich.py -i input.tsv -o enriched_output.tsv
import argparse
from protpen import enrich_utils
import csv

def run_enrichment_pipeline(input_tsv, output_tsv):
    # Step 1: Collect unique PDB IDs
    unique_pdb_ids = set()
    with open(input_tsv, newline="") as infile:
        reader = csv.DictReader(infile, delimiter="\t")
        for row in reader:
            target_field = row.get("target", "")
            for pdb_id in enrich_utils.extract_pdb_ids(target_field):
                unique_pdb_ids.add(pdb_id)

    unique_pdb_ids = list(unique_pdb_ids)
    print(f"Found {len(unique_pdb_ids)} unique PDB IDs in Foldseek results.")
    if not unique_pdb_ids:
        print("No PDB IDs found in the target column. Exiting.")
        return

    # Step 2: Map PDB → UniProt in batches
    print("Submitting batched UniProt mapping jobs...")
    pdb_to_uniprot = enrich_utils.map_pdb_to_uniprot_batched(unique_pdb_ids, batch_size=20)
    print(f"Retrieved UniProt mappings for {len(pdb_to_uniprot)} PDB IDs.")

    # Step 3: Gather UniProt info for each PDB ID
    uniprot_info_cache = {}
    pdb_to_info = {}
    for pdb_id, uniprot_ids in pdb_to_uniprot.items():
        desc_list = []
        interpro_list = []
        supfam_list = []
        for uid in uniprot_ids:
            if uid not in uniprot_info_cache:
                uniprot_info_cache[uid] = enrich_utils.get_uniprot_info(uid)
            info = uniprot_info_cache[uid]
            desc_list.append(info["description"])
            interpro_list.append(info["interpro"])
            supfam_list.append(info["supfam"])
        pdb_to_info[pdb_id] = {
            "description": ", ".join(desc_list) if desc_list else "n/a",
            "interpro": ", ".join(interpro_list) if interpro_list else "n/a",
            "supfam": ", ".join(supfam_list) if supfam_list else "n/a"
        }

    # Step 4: Mark unmapped PDBs as n/a
    for pdb_id in unique_pdb_ids:
        if pdb_id not in pdb_to_info:
            pdb_to_info[pdb_id] = {"description": "n/a", "interpro": "n/a", "supfam": "n/a"}

    # Step 5: Enrich the TSV
    print("Writing enriched TSV to", output_tsv)
    enrich_utils.enrich_tsv(input_tsv, output_tsv, pdb_to_info)
    print("Enrichment complete.")

def main():
    parser = argparse.ArgumentParser(
        description="CLI wrapper for enriching Foldseek TSVs with UniProt annotations."
    )
    parser.add_argument("-i", "--input", required=True, help="Input Foldseek TSV")
    parser.add_argument("-o", "--output", required=True, help="Output enriched TSV")
    args = parser.parse_args()

    run_enrichment_pipeline(args.input, args.output)

if __name__ == "__main__":
    main()
 