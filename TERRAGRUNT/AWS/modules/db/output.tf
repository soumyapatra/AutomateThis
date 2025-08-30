output "db_subnet_grp_name" {
  value = aws_db_subnet_group.db_subnet.name
}
output "rds_dns_name" {
  #value = module.rds[*].rds_dns_name
  value = values(module.rds)[*].rds_dns_name
}
output "rds_id" {
  #value = module.rds[*].rds_dns_name
  value = values(module.rds)[*].rds_id
}
