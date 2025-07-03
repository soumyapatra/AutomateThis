variable "eks_name" {
  description = "EKS Cluster Name"
}
variable "eks_endpoint" {
  description = "EKS Cluster Endpoint"
}
variable "eks_cert_auth_data" {
  description = "EKS cert_auth_data"
}
variable "bastion_role_arn" {
  description = "Bastion Role Arn"
}
variable "bastion_role_name" {
  description = "Bastion role name"
}
#variable "ng_role_arn" {
#  description = "NG Role ARN"
#}
variable "ng_name" {
  description = "NG Name"
}
