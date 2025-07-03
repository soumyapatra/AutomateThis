import requests
from requests.auth import HTTPBasicAuth

# Elasticsearch endpoint and authentication
es_url = "xxxxxxxxxxx"
username = "xxxxx"
password = "xxxxxxxxxxx"

# Get the indices information with authentication
response = requests.get(es_url, auth=HTTPBasicAuth(username, password))
indices_info = response.text

# Define the name pattern you are looking for
name_pattern = "xxxxxxxxfin-sbox-k8s-logs-primeops"

# Conversion function for size strings
def convert_size(size_str):
    size_str = size_str.lower()  # Convert to lowercase for uniformity
    if size_str.endswith('tb'):
        return float(size_str[:-2]) * 1024 ** 4
    elif size_str.endswith('gb'):
        return float(size_str[:-2]) * 1024 ** 3
    elif size_str.endswith('mb'):
        return float(size_str[:-2]) * 1024 ** 2
    elif size_str.endswith('kb'):
        return float(size_str[:-2]) * 1024
    elif size_str.endswith('b'):
        return float(size_str[:-1])
    else:
        raise ValueError(f"Unknown size format: {size_str}")

# Parse the indices information and filter by the name pattern
total_size = 0
for line in indices_info.splitlines()[1:]:  # Skip the header line
    parts = line.split()
    if len(parts) == 2 and name_pattern in parts[0]:
        size_str = parts[1]
        total_size += convert_size(size_str)

print(f"Total size of indices matching pattern '{name_pattern}': {total_size / (1024 ** 3):.2f} GB")
