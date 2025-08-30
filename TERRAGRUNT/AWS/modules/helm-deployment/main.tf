locals {
  filtered_services = {
    for service_name, service_config in var.service_vars["services"]:
      service_name => service_config if contains(var.service_list, service_name)
  }
  all_hosts = flatten([
    for service_name, service_config in local.filtered_services:
    [
        for host in service_config.hosts: {
        host = host.host
        paths = [
            for path in host.paths:{
                path = path.path
                service_name = service_name
                service_port = path.service_port
            }
        ]
        }
    ]
  ])
}

data "template_file" "helm_values" {
  template = "${file("${path.module}/svc_template.tpl")}"
  vars = {
    replica_count = var.replica_count
    image_name = var.image_name
    image_tag = var.image_tag
    image_repo = var.image_repo
    service_port = var.service_port
    target_port = var.target_port
    env = var.env
  }
}

resource "helm_release" "app" {
  name       = var.service_name
  chart      = "${path.module}/charts/appChart"
  values = [data.template_file.helm_values.rendered]
}

#resource "helm_release" "ingress" {
#  name       = "ingress"
#  chart      = "${path.module}/charts/ingChart"
#
#  values = yamlencode({
#    ingress_rules = local.ingress_rules
#  })
#}
