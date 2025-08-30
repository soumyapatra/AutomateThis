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
                path_type = path.path_type
                service_name = path.service_name
                service_port = path.service_port
            }
        ]
        }
    ]
  ])
}

data "aws_acm_certificate" "issued" {
  domain   = "dr.pyfn.in"
  statuses = ["ISSUED"]
}

resource "kubernetes_ingress_v1" "dynamic_ingress123" {
  metadata {
    name      = var.ingress_name
    namespace = var.namespace
    labels = {
      app = "LOS"
    }
    annotations = {
      "kubernetes.io/ingress.class" = "alb"
      "alb.ingress.kubernetes.io/certificate-arn" = data.aws_acm_certificate.issued.arn
      "alb.ingress.kubernetes.io/listen-ports" = jsonencode([{"HTTP": 80}, {"HTTPS":443}])
      "alb.ingress.kubernetes.io/healthcheck-path" =  "/healthcheck"
      "alb.ingress.kubernetes.io/scheme" = "internet-facing"
      "alb.ingress.kubernetes.io/target-type" = "instance"
      "alb.ingress.kubernetes.io/actions.ssl-redirect" = jsonencode({"Type": "redirect", "RedirectConfig":{ "Protocol": "HTTPS", "Port": "443", "StatusCode": "HTTP_301"}})
    }
  }
    spec {
        dynamic "rule" {
            for_each = local.all_hosts
            content {
                host = rule.value.host
                http {
                  dynamic "path" {
                    for_each = rule.value.paths
                    content {
                        path = path.value.path
                        path_type = path.value.path_type
                        backend {
                          service {
                            name = path.value.service_name
                            port {
                              number = path.value.service_port
                            }
                          }
                        }
                    }
                  }
                }
            }
        }
  }
}
