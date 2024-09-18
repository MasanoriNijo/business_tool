# config_reader.py
import json

def load_config(filename='config.json'):
    with open(filename, 'r') as file:
        config = json.load(file)
    return config
