output "oidc" {
  description = "The OIDC provider attributes for IAM Role for ServiceAccount"
  value = zipmap(
    ["url", "arn", "id"],
    [local.oidc["url"], local.oidc["arn"], local.oidc["id"]]
  )
}

output "endpoint" {
  value = aws_eks_cluster.master.endpoint
}

output "cert_auth_data" {
  value = aws_eks_cluster.master.certificate_authority[0].data
}

output "version" {
  value = aws_eks_cluster.master.version
}
output "eks_sg_id" {
  value = aws_eks_cluster.master.vpc_config[0].cluster_security_group_id
}

output "name" {
  value = aws_eks_cluster.master.name
}
output "helmconfig" {
  description = "The configurations map for Helm provider"
  sensitive   = true
  value = {
    host  = aws_eks_cluster.master.endpoint
    token = data.aws_eks_cluster_auth.master.token
    ca    = aws_eks_cluster.master.certificate_authority.0.data
  }
}
data "aws_eks_cluster_auth" "master" {
  name = aws_eks_cluster.master.name
}

locals {
  kubeconfig = <<KUBECONFIG


apiVersion: v1
clusters:
- cluster:
    server: ${aws_eks_cluster.master.endpoint}
    certificate-authority-data: ${aws_eks_cluster.master.certificate_authority.0.data}
  name: kubernetes
contexts:
- context:
    cluster: kubernetes
    user: aws
  name: aws
current-context: aws
kind: Config
preferences: {}
users:
- name: aws
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1alpha1
      command: aws-iam-authenticator
      args:
        - "token"
        - "-i"
        - "${aws_eks_cluster.master.name}"
KUBECONFIG
}

output "kubeconfig" {
  value = local.kubeconfig
}
