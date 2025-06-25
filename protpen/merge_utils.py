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

    # Full outer join: union of all query IDs
    all_queries = set(eggnog_data) | set(foldseek_data)

    # Construct the merged header
    merged_headers = ['query']
    if eggnog_headers:
        merged_headers += [eggnog_mapping[h] for h in eggnog_headers if h != 'query']
    if foldseek_headers:
        merged_headers += [foldseek_mapping[h] for h in foldseek_headers if h != 'query']

    # Merge rows
    merged_rows = []
    for query in sorted(all_queries):
        merged_row = {'query': query}
        egg_row = eggnog_data.get(query, {})
        fs_row = foldseek_data.get(query, {})

        for h in eggnog_headers:
            if h != 'query':
                merged_row[eggnog_mapping[h]] = egg_row.get(h, '')
        for h in foldseek_headers:
            if h != 'query':
                merged_row[foldseek_mapping[h]] = fs_row.get(h, '')

        merged_rows.append(merged_row)

    return merged_headers, merged_rows
