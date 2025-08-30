data "aws_eks_cluster_auth" "master" {
  name = var.eks_name
}

provider "kubectl" {
  host                   = var.eks_endpoint
  token                  = data.aws_eks_cluster_auth.master.token
  cluster_ca_certificate = base64decode(var.eks_cert_auth_data)
  load_config_file       = false
}

data "kubectl_filename_list" "manifests" {
    pattern = "./manifests/*.yml"
}

data "aws_acm_certificate" "issued" {
  domain   = "dr.pyfn.in"
  statuses = ["ISSUED"]
}

data "kubectl_path_documents" "ingress" {
    pattern = "./*.yml"
    vars = {
        cert-arn = data.aws_acm_certificate.issued.arn
    }
}

resource "kubectl_manifest" "ingress" {
    for_each  = toset(data.kubectl_path_documents.ingress.documents)
    yaml_body = each.value
    depends_on = [kubectl_manifest.test]
}

resource "kubectl_manifest" "test" {
    count = length(data.kubectl_filename_list.manifests.matches)
    yaml_body = file(element(data.kubectl_filename_list.manifests.matches, count.index))
    wait_for_rollout = false
}
