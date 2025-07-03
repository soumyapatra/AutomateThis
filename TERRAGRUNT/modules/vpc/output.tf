output "private_subnets" {
  description = "List of IDs of private subnets"
  value       = aws_subnet.private[*].id
}

output "public_subnets" {
  description = "List of IDs of public subnets"
  value       = aws_subnet.public[*].id
}

output "db_subnets" {
  description = "List of IDs of public subnets"
  value       = aws_subnet.db[*].id
}

output "vpc_id" {
  description = "The ID of the VPC"
  value       = try(aws_vpc.this[0].id, var.vpc_id)
}

output "bastion_public_ip" {
  value = aws_instance.bastion[*].public_ip
}

output "bastion_sg_id" {
  value = aws_security_group.bastion.id
}

output "bastion_role_arn" {
  value = aws_iam_role.bastion_role.arn
}

output "bastion_role_name" {
  value = aws_iam_role.bastion_role.name
}
