data "aws_caller_identity" "current" {}

locals {
  service_params = {
    for service_name in var.service_list :
    service_name => try(var.service_vars["services"][service_name]["deployment"], null)
  }
  image_repo = join(".", compact(["${data.aws_caller_identity.current.account_id}","dkr","ecr","${var.region}","amazonaws","com"]))
}

data "aws_eks_cluster_auth" "master" {
  name = var.eks_name
}

provider "helm" {
  kubernetes {
    host                   = var.eks_endpoint
    token                  = data.aws_eks_cluster_auth.master.token
    cluster_ca_certificate = base64decode(var.eks_cert_auth_data)
  }
}

provider "kubernetes" {
  host                   = var.eks_endpoint
  token                  = data.aws_eks_cluster_auth.master.token
  cluster_ca_certificate = base64decode(var.eks_cert_auth_data)
}

module helm {
  source = "../helm-deployment"
  for_each = { for k, v in local.service_params : k => v if v != null }
  replica_count = each.value["replica_count"]
  service_name = each.value["name"]
  service_port = each.value["service_port"]
  target_port = each.value["target_port"]
  image_name = each.value["image_name"]
  image_tag = each.value["image_tag"]
  image_repo = "${local.image_repo}"
  env = var.env
  service_list = var.service_list
  service_vars = var.service_vars
}

module ing {
  source = "../ingress"
  service_list = var.service_list
  service_vars = var.service_vars
  ingress_name = "xxxxxxxxfin-sbox-external-ingress"
}
