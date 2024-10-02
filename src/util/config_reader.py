# config_reader.py
import json

def load_config(filename='conf/config.json'):
    with open(filename, 'r', encoding='utf-8') as file:
        config = json.load(file)
    return config
