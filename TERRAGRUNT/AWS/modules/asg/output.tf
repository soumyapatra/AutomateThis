output "eks_worker_role_arn" {
  value = aws_iam_role.worker-node.arn
}