import requests
from grafana_api.grafana_face import GrafanaFace
import json

URL = "http://10.80.110.221:3000"

header = {'Authorization': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'}
response = requests.get(url=f'{URL}/api/dashboards/home', headers=header)

query = requests.get(url=f'{URL}/api/search?folderIds=0&query=&starred=false', headers=header)
var = query.json()
for item in var:
    print(item)
    title = item['title'].replace("/", "_")
    title = title.replace(" ", "_")
    #print(title)

    uid = item['uid']
    get_dash = requests.get(url=f'{URL}/api/dashboards/uid/{uid}', headers=header)
    dash_json = get_dash.json()
    #with open(f'{title}.json', "w") as outfile:
    #    json.dump(dash_json, outfile)
    #print(dash_json)

grafana_api = GrafanaFace(auth='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
                          host='10.80.110.221:3000')
