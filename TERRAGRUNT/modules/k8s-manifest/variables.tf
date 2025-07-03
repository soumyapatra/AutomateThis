variable "eks_name" {
  description = "EKS Cluster Name"
}
variable "eks_endpoint" {
  description = "EKS Cluster Endpoint"
}
variable "eks_cert_auth_data" {
  description = "EKS cert_auth_data"
}
variable "rds_id" {
  description = "RDS DB ID"
}
variable "ng_id" {
  description = "NodeGroup ID"
}
variable "sub_domain_name" {
  description = "Route53 Subdomain"
}
