import boto3
import sys
import json

cw = boto3.client("cloudwatch")
ec2 = boto3.client("ec2")

if len(sys.argv) != 2:
    sys.exit("Please enter the environment parameter(Development, Staging, Tqa, Production, \"Shared Tools\")")
environment = sys.argv[1]

x, y = [0, 0]
y_coor_inc_per_ins = 15
width, height = [6, 6]
descriptor_width = 24
widget_count = 0
widget_dashboard_limit = 450 / 2
widgets = []
instance_name = ""
instance_id = ""
instance_type = ""
dashboard_name = ""
dashboard_count = 1


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>#
# >>>>>>>>>>>>>>>>>>>>> Function Definitions >>>>>>>>>>>>>>>>>>>>>>>>#
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>#
def extract_instance_info(i):
    global instance_name, instance_id, instance_type

    for t in i["Tags"]:
        if t["Key"] == "Name":
            instance_name = t["Value"]

        instance_id = i["InstanceId"]
        instance_type = i["InstanceType"]


def add_descriptor_widget():
    global widget_count

    descriptor = {"type": "text",
                  "x": x,
                  "y": y,
                  "width": descriptor_width,
                  "height": height / 2,
                  "properties": {"markdown": "\n# " + instance_name + "\n"
                                 }
                  }

    widgets.append(descriptor)
    widget_count += 1


def add_memory_widget():
    global widget_count

    memory_widget = {"type": "metric",
                     "x": x,
                     "y": y + 3,
                     "width": width,
                     "height": height,
                     "properties": {"view": "timeSeries",
                                    "stacked": False,
                                    "metrics": [["CWAgent", "MEM_AVAILABLE", "InstanceId", instance_id, "InstanceType",
                                                 instance_type],
                                                [".", "MEM_TOTAL", ".", ".", ".", "."],
                                                [".", "MEM_USED", ".", ".", ".", "."]
                                                ],
                                    "region": "eu-west-1",
                                    "title": instance_name + " Server - Memory"
                                    }
                     }

    widgets.append(memory_widget)
    widget_count += 1


def add_storage_widget():
    global widget_count

    storage_widget = {"type": "metric",
                      "x": x + 6,
                      "y": y + 3,
                      "width": width,
                      "height": height,
                      "properties": {"view": "timeSeries",
                                     "stacked": False,
                                     "metrics": [["CWAgent", "DISK_USED", "InstanceId", instance_id, "InstanceType",
                                                  instance_type]
                                                 ],
                                     "region": "eu-west-1",
                                     "title": instance_name + " Server - Storage"
                                     }
                      }

    widgets.append(storage_widget)
    widget_count += 1


def add_cpu_widget():
    global widget_count

    cpu_widget = {"type": "metric",
                  "x": x + 12,
                  "y": y + 3,
                  "width": width,
                  "height": height,
                  "properties": {"view": "timeSeries",
                                 "stacked": False,
                                 "metrics": [["CWAgent", "CPU_USAGE_IDLE", "InstanceId", instance_id, "InstanceType",
                                              instance_type],
                                             [".", "CPU_USAGE_IOWAIT", ".", ".", ".", "."]
                                             ],
                                 "region": "eu-west-1",
                                 "title": instance_name + " Server - CPU Usage"
                                 }
                  }

    widgets.append(cpu_widget)
    widget_count += 1


def add_process_widget():
    global widget_count

    process_widget = {"type": "metric",
                      "x": x + 18,
                      "y": y + 3,
                      "width": width,
                      "height": height,
                      "properties": {"view": "timeSeries",
                                     "stacked": False,
                                     "metrics": [
                                         ["CWAgent", "PROCESSES_RUNNING", "InstanceId", instance_id, "InstanceType",
                                          instance_type],
                                         [".", "PROCESSES_BLOCKED", ".", ".", ".", "."],
                                         [".", "PROCESSES_ZOMBIES", ".", ".", ".", "."]
                                         ],
                                     "region": "eu-west-1",
                                     "title": instance_name + " Server - Processes"
                                     }
                      }

    widgets.append(process_widget)
    widget_count += 1


def add_diskio_widget():
    global widget_count

    diskio_widget = {"type": "metric",
                     "x": x,
                     "y": y + 9,
                     "width": width,
                     "height": height,
                     "properties": {"view": "timeSeries",
                                    "stacked": False,
                                    "metrics": [
                                        ["CWAgent", "DISKIO_READ_TIME", "InstanceId", instance_id, "InstanceType",
                                         instance_type],
                                        [".", "DISKIO_WRITE_TIME", ".", ".", ".", "."]
                                        ],
                                    "region": "eu-west-1",
                                    "title": instance_name + " Server - DiskIO"
                                    }
                     }

    widgets.append(diskio_widget)
    widget_count += 1


def add_diskinodes_widget():
    global widget_count

    diskinodes_widget = {"type": "metric",
                         "x": x + 6,
                         "y": y + 9,
                         "width": width,
                         "height": height,
                         "properties": {"view": "timeSeries",
                                        "stacked": False,
                                        "metrics": [
                                            ["CWAgent", "DISK_INODES_FREE", "InstanceId", instance_id, "InstanceType",
                                             instance_type],
                                            [".", "DISK_INODES_TOTAL", ".", ".", ".", "."],
                                            [".", "DISK_INODES_USED", ".", ".", ".", "."]
                                            ],
                                        "region": "eu-west-1",
                                        "title": instance_name + " Server - Disk Inodes"
                                        }
                         }

    widgets.append(diskinodes_widget)
    widget_count += 1


def add_diskioinprogress_widget():
    global widget_count

    diskioinprogress_widget = {"type": "metric",
                               "x": x + 12,
                               "y": y + 9,
                               "width": width,
                               "height": height,
                               "properties": {"view": "timeSeries",
                                              "stacked": False,
                                              "metrics": [
                                                  ["CWAgent", "DISKIO_IOPS_IN_PROGRESS", "InstanceId", instance_id,
                                                   "InstanceType", instance_type]
                                                  ],
                                              "region": "eu-west-1",
                                              "title": instance_name + " Server - DiskIO In Progress"
                                              }
                               }

    widgets.append(diskioinprogress_widget)
    widget_count += 1


def add_netstat_widget():
    global widget_count

    netstat_widget = {"type": "metric",
                      "x": x + 18,
                      "y": y + 9,
                      "width": width,
                      "height": height,
                      "properties": {"view": "timeSeries",
                                     "stacked": False,
                                     "metrics": [
                                         ["CWAgent", "NETSTAT_TCP_SYN_SENT", "InstanceId", instance_id, "InstanceType",
                                          instance_type],
                                         [".", "NETSTAT_TCP_LISTEN", ".", ".", ".", "."],
                                         [".", "NETSTAT_TCP_ESTABLISHED", ".", ".", ".", "."]
                                         ],
                                     "region": "eu-west-1",
                                     "title": instance_name + " Server - Netstat TCP"
                                     }
                      }

    widgets.append(netstat_widget)
    widget_count += 1


def describe_instances():
    global instances

    print("Gathering instances from " + environment + " environment...")

    instances = ec2.describe_instances(
        Filters=[{'Name': 'tag:Environment', 'Values': [environment]}
                 ])

    print("DONE!")


def create_or_update_dashboard(dn):
    global widgets

    body = {'widgets': widgets}

    body_j = json.dumps(body)

    cw.put_dashboard(DashboardName=dn,
                     DashboardBody=body_j)

    print("Dashboard " + dn + " is created!")


def list_dashboards(dn):
    return cw.list_dashboards(DashboardNamePrefix=dn)


def delete_dashboard(dn):
    for x in list_dashboards(dn)["DashboardEntries"]:
        print("Deleting old dashboard " + x["DashboardName"] + "...")
        cw.delete_dashboards(DashboardNames=[x["DashboardName"]])
        print("DONE!")


def set_dashboard_names():
    global environment, dashboard_name

    if environment == "Development":
        dashboard_name = environment + "_Nidavellir"
    elif environment == "Staging":
        dashboard_name = environment + "_Vanaheim"
    elif environment == "Tqa":
        dashboard_name = environment + "_Niflheimr"
    elif environment == "Production":
        dashboard_name = environment + "_Valhalla"
    elif environment == "Shared Tools":
        dashboard_name = "SharedTools" + "_Muspelheim"
    else:
        sys.exit("Please enter a valid environment(Development, Staging, Tqa, Production, \"Shared Tools\")")


# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<#
# <<<<<<<<<<<<<<<<<<<<<< Function Definitions <<<<<<<<<<<<<<<<<<<<<<<#
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<#

set_dashboard_names()
delete_dashboard(dashboard_name)
describe_instances()

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>#
# >>>>>>>>>>>>>>>>>>>>>>>> Append Widgets >>>>>>>>>>>>>>>>>>>>>>>>>>>#
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>#
print("Creating/Updating dashboard for " + environment + "...")
for r in instances['Reservations']:
    for i in r['Instances']:

        extract_instance_info(i)

        add_descriptor_widget()

        add_memory_widget()
        add_storage_widget()
        add_cpu_widget()
        add_process_widget()
        add_diskio_widget()
        add_diskinodes_widget()
        add_diskioinprogress_widget()
        add_netstat_widget()

        if widget_count > widget_dashboard_limit:
            create_or_update_dashboard(dashboard_name + "-" + str(dashboard_count))
            dashboard_count += 1;
            widgets = []
            widget_count = 0
            y = 0
        else:
            y += y_coor_inc_per_ins
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<#
# <<<<<<<<<<<<<<<<<<<<<<<<< Append Widgets <<<<<<<<<<<<<<<<<<<<<<<<<<#
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<#
if dashboard_count == 1:
    create_or_update_dashboard(dashboard_name)
else:
    create_or_update_dashboard(dashboard_name + "-" + str(dashboard_count))
print("DONE!")