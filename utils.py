
import yaml

def read_one_block_of_yaml_data(filename):
    with open(f'{filename}','r') as f:
        return yaml.safe_load(f)