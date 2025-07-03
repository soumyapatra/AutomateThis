output "kubernetes_config_map" {
  value = kubernetes_config_map.aws-auth.data
}
output "ng_role_arn" {
  value = aws_iam_role.eks_nodes.arn
}
