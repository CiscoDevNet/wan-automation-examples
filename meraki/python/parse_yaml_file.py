# =========================================================================
# File: parse_yaml_file.py
# Revision 1.0 - 10/21/2025
# =========================================================================
#
# Description:
#   This module opens and parses a YAML file, passed in as a variable,
#   which defines the payload for API calls. It converts the YAML file
#   into a dictionary object, which is returned
#

import yaml
import sys
import json

def parse(payload_file):
    
    try:
      f = open(payload_file, 'r')
      payload_dict = yaml.safe_load(f)
      # Uncomment to view the payload as json 
      # print(json.dumps(payload_dict, indent=2))
      return payload_dict
    
    except FileNotFoundError:
      print("File not found.")

if __name__ == '__main__':
    print(parse(sys.argv[1]))