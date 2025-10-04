import json
import csv

def json_to_csv(json_file, csv_file):
    with open(json_file, 'r', encoding='utf-8') as jf:
        data = [json.loads(line) for line in jf]

    if not data:
        print("No data found in JSON file.")
        return

    # Get all unique keys for CSV header
    keys = set()
    for item in data:
        keys.update(item.keys())
    keys = list(keys)

    with open(csv_file, 'w', newline='', encoding='utf-8') as cf:
        writer = csv.DictWriter(cf, fieldnames=keys)
        writer.writeheader()
        for item in data:
            writer.writerow(item)

if __name__ == "__main__":
    # Example usage:
    json_to_csv('train.jsonl', 'fever_data.csv')