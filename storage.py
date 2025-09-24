#storage.py

import json
import csv

def save_to_json(data, filename: str):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def save_to_csv(matches: list, filename: str):
    if not matches:
        return
    keys = matches[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(matches)