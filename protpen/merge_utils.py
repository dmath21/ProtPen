# protpen/merge_utils.py

import csv

def read_tsv(filepath):
    data = {}
    with open(filepath, 'r', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        headers = reader.fieldnames
        for row in reader:
            query = row.get('query')
            if query:
                data[query] = row
    return data, headers

def create_header_mapping(headers, prefix):
    return {h: h if h == 'query' else f"{prefix}_{h}" for h in headers}

def merge_data(eggnog_data, eggnog_headers, foldseek_data, foldseek_headers):
    eggnog_mapping = create_header_mapping(eggnog_headers, "eggnog")
    foldseek_mapping = create_header_mapping(foldseek_headers, "foldseek")

    filtered_eggnog_data = {q: eggnog_data[q] for q in foldseek_data if q in eggnog_data}

    merged_headers = ['query'] + [eggnog_mapping[h] for h in eggnog_headers if h != 'query'] + \
                     [foldseek_mapping[h] for h in foldseek_headers if h != 'query']

    merged_rows = []
    for query in sorted(foldseek_data):
        merged_row = {'query': query}
        egg_row = filtered_eggnog_data.get(query, {})
        fs_row = foldseek_data[query]

        for h in eggnog_headers:
            if h != 'query':
                merged_row[eggnog_mapping[h]] = egg_row.get(h, '')
        for h in foldseek_headers:
            if h != 'query':
                merged_row[foldseek_mapping[h]] = fs_row.get(h, '')

        merged_rows.append(merged_row)

    return merged_headers, merged_rows
