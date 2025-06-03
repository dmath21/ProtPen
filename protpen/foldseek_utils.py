# protpen/foldseek_utils.py
import os
import pandas as pd

def extract_protein_ids(fasta_file):
    protein_ids = set()
    with open(fasta_file, "r") as f:
        for line in f:
            if line.startswith(">"):
                protein_ids.add(line.strip().split()[0][1:])
    return protein_ids


def consolidate_foldseek_results(input_dir, query_fasta, top_x=5):
    query_proteins = extract_protein_ids(query_fasta)
    consolidated_results = {}

    for file in os.listdir(input_dir):
        if file.endswith(".tsv"):
            file_path = os.path.join(input_dir, file)
            df = pd.read_csv(file_path, sep="\t")

            df['evalue'] = pd.to_numeric(df['evalue'], errors='coerce')
            df = df[df['evalue'] > 0]
            df = df[df['query'].isin(query_proteins)]
            df = df.sort_values(by='evalue', ascending=True)
            df = df.groupby('query').head(top_x)

            if not df.empty:
                for query, sub_df in df.groupby('query'):
                    concatenated_values = sub_df.drop(columns=['query']).apply(
                        lambda col: "||".join(map(str, col)), axis=0
                    )
                    consolidated_results[query] = concatenated_values

    if consolidated_results:
        consolidated_df = pd.DataFrame.from_dict(consolidated_results, orient='index').reset_index()
        consolidated_df.rename(columns={'index': 'query'}, inplace=True)
        return consolidated_df
    else:
        return pd.DataFrame(columns=["query"])
