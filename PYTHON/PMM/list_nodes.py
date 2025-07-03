import requests
from requests.auth import HTTPBasicAuth
import json

PMM_SERVER = "pmm-server.stage-rc.in"


def list_node():
    try:
        url = "http://{}/v1/inventory/Nodes/List".format(PMM_SERVER)
        params = {'node_type': 'GENERIC_NODE'}
        r = requests.post(url=url, json=params, auth=HTTPBasicAuth('admin', 'admin'))
        data = r.json()
        json_data = json.dumps(data)
        data1 = json.loads(json_data)
        for item in data1["generic"]:
            if item["node_name"] == "abc123-mysql-slave1":
                return item["node_id"]
    except requests.Timeout as e:
        print("Not able to connect to {}".format(PMM_SERVER))
        exit()


def remove_node(id):
    try:
        url = "http://{}/v1/inventory/Nodes/Remove".format(PMM_SERVER)
        header = {'accept': 'application/json', 'Content-Type': 'application/json'}
        params = {
            "node_id": id,
            "force": True
        }
        r = requests.post(url=url, json=params, auth=HTTPBasicAuth('admin', 'admin'), headers=header)
        url_request = r.request.url
        data = r.json()
        print("DONE")
    except Exception as e:
        print("Failed: ", e)


print(list_node())