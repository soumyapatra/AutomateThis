variable "eks_name" {
  description = "EKS Cluster Name"
}
variable "eks_endpoint" {
  description = "EKS Cluster Endpoint"
}
variable "eks_cert_auth_data" {
  description = "EKS cert_auth_data"
}
variable "region" {
  description = "AWS REGION"
}
variable "vpc_id" {
  description = "VPC ID"
}
variable "name" {
  description = "Cluster Name"
}
variable "oidc_provider" {
  description = "OIDC Provider"
}

variable "oidc_arn" {
  description = "OIDC ARN"
}
