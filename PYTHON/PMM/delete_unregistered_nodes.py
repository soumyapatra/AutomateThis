import boto3
import requests
import json
from requests.auth import HTTPBasicAuth

PMM_SERVER = "10.24.207.205"


def get_mysql_service(node_id):
    try:
        url = "http://{}/v1/inventory/Services/List".format(PMM_SERVER)
        param = {'node_id': node_id, "service_type": "MYSQL_SERVICE"}
        response = requests.post(url=url, json=param, auth=HTTPBasicAuth('admin', 'admin'))
        response_json = response.json()
        dump = json.dumps(response_json)
        result = json.loads(dump)
        for service in result["mysql"]:
            if service["node_id"] == node_id:
                service_id = service["service_id"]
                return service_id
    except KeyError as e:
        return False
    except requests.Timeout as e:
        print("Not able to connect to {}".format(PMM_SERVER))


def remove_service(id):
    try:
        url = "http://{}/v1/inventory/Services/Remove".format(PMM_SERVER)
        header = {'accept': 'application/json', 'Content-Type': 'application/json'}
        params = {
            "service_id": id,
            "force": True
        }
        r = requests.post(url=url, json=params, auth=HTTPBasicAuth('admin', 'admin'), headers=header)
        url_request = r.request.url
        data = r.json()
        print("DONE")
    except Exception as e:
        print("Failed: ", e)
    except requests.Timeout as e:
        print("Not able to connect to url {}".format(PMM_SERVER))


def get_mongodb_service(node_id):
    try:
        url = "http://{}/v1/inventory/Services/List".format(PMM_SERVER)
        param = {'node_id': node_id, "service_type": "MONGODB_SERVICE"}
        response = requests.post(url=url, json=param, auth=HTTPBasicAuth('admin', 'admin'))
        response_json = response.json()
        dump = json.dumps(response_json)
        result = json.loads(dump)
        for service in result["mongodb"]:
            if service["node_id"] == node_id:
                service_id = service["service_id"]
                return service_id
    except KeyError as e:
        return False
    except requests.Timeout as e:
        print("Not able to connect to {}".format(PMM_SERVER))


def get_node_id(ip):
    try:
        url = "http://{}/v1/inventory/Nodes/List".format(PMM_SERVER)
        params = {'node_type': 'GENERIC_NODE'}
        r = requests.post(url=url, json=params, auth=HTTPBasicAuth('admin', 'admin'))
        data = r.json()
        json_data = json.dumps(data)
        data1 = json.loads(json_data)
        for item in data1["generic"]:
            if item["address"] == ip:
                node_id = item["node_id"]
                return node_id
        return False
    except requests.Timeout as e:
        print("Not able to connect to {}".format(PMM_SERVER))
        exit()


def get_instance_ips(region):
    ec2 = boto3.resource('ec2', region_name=region)
    instances = ec2.instances.all()
    ips = []
    for instance in instances:
        ips.append(instance.private_ip_address)
    return ips


def get_agents(id):
    try:
        url = "http://{}/v1/inventory/Agents/List".format(PMM_SERVER)
        agent_dict = dict()
        param = {'node_id': id, "agent_type": "NODE_EXPORTER"}
        response = requests.post(url=url, json=param, auth=HTTPBasicAuth('admin', 'admin'))
        response_json = response.json()
        dump = json.dumps(response_json)
        result = json.loads(dump)
        for item in result['node_exporter']:
            agent_dict["agent_id"] = item["agent_id"]
            agent_dict["pmm_agent_id"] = item["pmm_agent_id"]
            return agent_dict
    except Exception as e:
        print("cant find agents for node: ", node_id)
        return False
    except requests.Timeout as e:
        print("Not able to connect to {}".format(PMM_SERVER))


def get_node_ips():
    try:
        ips = []
        url = "http://{}/v1/inventory/Nodes/List".format(PMM_SERVER)
        params = {'node_type': 'GENERIC_NODE'}
        r = requests.post(url=url, json=params, auth=HTTPBasicAuth('admin', 'admin'))
        data = r.json()
        json_data = json.dumps(data)
        data1 = json.loads(json_data)
        for item in data1["generic"]:
            ips.append(item["address"])
        return ips

    except requests.Timeout as e:
        print("Not able to connect to {}".format(PMM_SERVER))
        exit()


def remove_agent(id):
    try:
        url = "http://{}/v1/inventory/Agents/Remove".format(PMM_SERVER)
        header = {'accept': 'application/json', 'Content-Type': 'application/json'}
        params = {
            "agent_id": id,
            "force": True
        }
        r = requests.post(url=url, json=params, auth=HTTPBasicAuth('admin', 'admin'), headers=header)
        url_request = r.request.url
        data = r.json()
        print("DONE")
    except Exception as e:
        print("Failed", e)


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


instance_ips = get_instance_ips('ap-south-1')
node_ips = get_node_ips()

for ip in node_ips:
    if ip not in instance_ips:
        if get_node_id(ip):
            node_id = get_node_id(ip)
            print("Got node ID: ", node_id)
            if get_mysql_service(node_id):
                service_id = get_mysql_service(node_id)
                print("Got Mysql service ID: ", service_id, "Removing !!")
                remove_service(service_id)
            elif get_mongodb_service(node_id):
                service_id = get_mongodb_service(node_id)
                print("Got MongoDB service ID: ", service_id, "Removing !!")
                remove_service(service_id)
            else:
                print("Mysql/MongoDB service not found")
            if get_agents(node_id):
                agents = get_agents(node_id)
                print("Removing agent: ", agents["agent_id"])
                remove_agent(agents["agent_id"])
                print("Removing pmm agent: ", agents["pmm_agent_id"])
                remove_agent(agents["pmm_agent_id"])
            print("Removing Node")
            remove_node(node_id)
        else:
            print("Node not found for IP: ", ip)
