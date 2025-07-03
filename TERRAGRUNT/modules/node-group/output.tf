#output "remote_sg_id" {
#  value = aws_eks_node_group.node.remote_access_security_group_id
#}

output "ng_id" {
  value = aws_eks_node_group.node.id
}
