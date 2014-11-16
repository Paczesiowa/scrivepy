import json
from os import path


global config
config = {}

try:
    with open(path.join('tests', 'test_config.json'), 'r') as f:
        config['test_api_server'] = json.load(f)
except IOError:
    pass
