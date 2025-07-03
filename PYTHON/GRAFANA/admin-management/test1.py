from grafana_api.grafana_face import GrafanaFace
import json
import requests
from requests.auth import HTTPBasicAuth

url = "http://10.80.130.117:3000/api/dashboards/home"
headers = {"Authorization": "Bearer xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}

response = requests.get(url=url, headers=headers)
print(response.json())
print(response.status_code)

url = "http://10.80.130.117:3000/api/auth/keys"
response = requests.get(url=url, headers=headers)
print(response.json())
print(response.status_code)

url = "http://10.80.130.117:3000/api/users?perpage=10&page=1"
response = requests.get(url=url, headers=headers, auth=HTTPBasicAuth('admin', 'admin'))
print(response.json())
print(response.status_code)

# grafana_api = GrafanaFace(auth='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', host='xxxxxxxxx:xxxxxxxx')
# with open("all_instance.json") as f:
#    data = json.load(f)

# print(data)
# print(grafana_api.search.search_dashboards(tag='sample'))
# print(grafana_api.teams.search_teams("Alpha"))
# print(grafana_api.admin.)

# print(grafana_api.folder.get_all_folders())
# grafana_api.dashboard.update_dashboard(dashboard={'dashboard': data, 'folderId': 29, 'overwrite': True})
