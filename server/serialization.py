import json


def result2csv(records, column_names, include_header):
    if include_header:
        records.insert(0, column_names)
    list_of_str = [','.join(map(str, rec)) for rec in records]
    csv = '\n'.join(list_of_str)
    return csv


def result2json(records, column_names):
    results = []
    for record in records:
        results.append({c: str(record[i]) for (i, c) in enumerate(column_names)})
    return json.dumps(results)
