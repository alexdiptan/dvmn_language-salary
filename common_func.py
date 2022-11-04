import json


def save_to_json(json_data: dict, file_name: str):
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(json.dumps(json_data, ensure_ascii=False, indent=2))


def get_json_data_from_file(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        return json_data
