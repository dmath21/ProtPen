import csv
import argparse

def read_tsv(filepath):
    """
    Reads a TSV file and returns a dictionary mapping query IDs to their row (as a dict)
    along with the header fieldnames.
    """
    data = {}
    with open(filepath, 'r', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        headers = reader.fieldnames
        for row in reader:
            query = row.get('query')
            if query:
                data[query] = row  # Store row by query ID
    return data, headers

def create_header_mapping(headers, prefix):
    """
    Creates a mapping for headers.
    For any header (except 'query'), rename it to '<prefix>_<header>'.
    """
    mapping = {}
    for h in headers:
        if h == 'query':
            mapping[h] = h
        else:
            mapping[h] = f"{prefix}_{h}"
    return mapping

def merge_data(eggnog_data, eggnog_headers, foldseek_data, foldseek_headers):
    """
    Merges EggNOG data with Foldseek data.
    Only includes EggNOG rows that match Foldseek queries.
    """
    # Create header mappings for both EggNOG and Foldseek:
    eggnog_mapping = create_header_mapping(eggnog_headers, "eggnog")
    foldseek_mapping = create_header_mapping(foldseek_headers, "foldseek")

    # Filter EggNOG data for only queries found in Foldseek
    filtered_eggnog_data = {query: eggnog_data[query] for query in foldseek_data.keys() if query in eggnog_data}

    # Build merged headers: query + EggNOG fields (prefixed) + Foldseek fields (prefixed)
    merged_headers = ['query'] + [eggnog_mapping[h] for h in eggnog_headers if h != 'query'] \
                     + [foldseek_mapping[h] for h in foldseek_headers if h != 'query']

    # Merge rows for only the filtered queries
    merged_rows = []
    for query in sorted(foldseek_data.keys()):  # Process only queries found in Foldseek
        merged_row = {'query': query}
        egg_row = filtered_eggnog_data.get(query, {})
        fs_row = foldseek_data[query]

        # Fill EggNOG columns (using the eggnog mapping)
        for h in eggnog_headers:
            if h != 'query':
                merged_row[eggnog_mapping[h]] = egg_row.get(h, '')

        # Fill Foldseek columns (using the foldseek mapping)
        for h in foldseek_headers:
            if h != 'query':
                merged_row[foldseek_mapping[h]] = fs_row.get(h, '')

        merged_rows.append(merged_row)

    return merged_headers, merged_rows

def main():
    parser = argparse.ArgumentParser(
        description="Merge EggNOG-mapper and Foldseek TSV files, filtering EggNOG results for Foldseek queries."
    )
    parser.add_argument("eggnog", help="Path to the EggNOG-mapper TSV file")
    parser.add_argument("foldseek", help="Path to the Foldseek TSV file")
    parser.add_argument("output", help="Path to the output merged TSV file")
    args = parser.parse_args()

    # Read input files
    eggnog_data, eggnog_headers = read_tsv(args.eggnog)
    foldseek_data, foldseek_headers = read_tsv(args.foldseek)

    # Merge the data (EggNOG is filtered for query proteins)
    merged_headers, merged_rows = merge_data(eggnog_data, eggnog_headers, foldseek_data, foldseek_headers)

    # Write the output TSV file with clear header prefixes
    with open(args.output, 'w', newline='') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=merged_headers, delimiter='\t')
        writer.writeheader()
        writer.writerows(merged_rows)

    print(f"Merged {len(merged_rows)} rows written to {args.output}")

if __name__ == '__main__':
    main()
