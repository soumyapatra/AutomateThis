output "master_sg_id" {
  value = aws_security_group.master.id
}

output "worker_sg_id" {
  value = aws_security_group.worker.id
}

output "rds_sg_id" {
  value = aws_security_group.rds.id
}
