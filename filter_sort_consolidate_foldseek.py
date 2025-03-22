import pandas as pd
import os
import sys

"""
This script filters, sorts, and consolidates Foldseek results from multiple TSV files in a specified directory.
It reads TSV files, filters out entries with an evalue of 0, sorts by evalue, and consolidates the top X scoring proteins per query.

Args:
    input_directory: Directory containing Foldseek TSV files.
    output_file: Path to save the consolidated TSV file.
    query_fasta: Path to the FASTA file containing query protein IDs.
    top_x: Number of top scoring proteins to keep per query (default is 5).
"""

# Function to extract protein IDs from a FASTA file
def extract_protein_ids(fasta_file):
    protein_ids = set()
    with open(fasta_file, "r") as f:
        for line in f:
            if line.startswith(">"):
                protein_ids.add(line.strip().split()[0][1:])  # Remove '>' and take first word as ID
    return protein_ids

# Check if correct number of arguments is provided
if len(sys.argv) < 4 or len(sys.argv) > 5:
    print("Usage: sort_consolidate_foldseek_results.py <input_directory> <output_file> <query_fasta> [top_x]")
    sys.exit(1)

# Get input directory, output file, query FASTA file, and optional top_x from system arguments
input_dir = sys.argv[1]
output_file = sys.argv[2]
query_fasta = sys.argv[3]
top_x = int(sys.argv[4]) if len(sys.argv) == 5 else 5  # Default to 5 if not specified

# Extract protein IDs from the FASTA file
query_proteins = extract_protein_ids(query_fasta)

# Dictionary to store consolidated results
consolidated_results = {}

# Iterate over all TSV files in the directory
for file in os.listdir(input_dir):
    if file.endswith(".tsv"):
        file_path = os.path.join(input_dir, file)
        
        # Read the TSV file
        df = pd.read_csv(file_path, sep="\t")
        
        # Ensure the evalue column is numeric
        df['evalue'] = pd.to_numeric(df['evalue'], errors='coerce')
        
        # Remove rows where evalue is 0
        df = df[df['evalue'] > 0]
        
        # Filter results to include only those for proteins in the query FASTA
        df = df[df['query'].isin(query_proteins)]
        
        # Sort by evalue in ascending order
        df = df.sort_values(by='evalue', ascending=True)
        
        # Take only the top X scoring proteins per query
        df = df.groupby('query').head(top_x)
        
        if not df.empty:
            for query, sub_df in df.groupby('query'):
                # Concatenate all columns except 'query' using "||"
                concatenated_values = sub_df.drop(columns=['query']).apply(lambda col: "||".join(map(str, col)), axis=0)

                # Store in dictionary to ensure unique query entries
                consolidated_results[query] = concatenated_values

# Convert dictionary to DataFrame
if consolidated_results:
    consolidated_df = pd.DataFrame.from_dict(consolidated_results, orient='index').reset_index()
    consolidated_df.rename(columns={'index': 'query'}, inplace=True)

    # Save the consolidated DataFrame to a TSV file
    consolidated_df.to_csv(output_file, sep="\t", index=False)

    print(f"Filtered top {top_x} sorted results (excluding evalue 0) consolidated and saved to {output_file}")
else:
    print("No valid results found. No output file generated.")
