output "db_instance_arn" {
  value = aws_db_instance.db.arn
}
output "rds_dns_name" {
  value = aws_db_instance.db.address
}
output "rds_id" {
  value = aws_db_instance.db.id
}
output "rds_endpoint" {
  value = aws_db_instance.db.endpoint
}
