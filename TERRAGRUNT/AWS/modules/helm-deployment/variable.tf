variable "replica_count" {
 type = string
}
variable "service_name" {
 type = string  
}
variable "service_port" {
 type = string 
}
variable "target_port" {
 type = string 
}
variable "image_name" {
  type = string
}
variable "image_tag" {
  type = string
}
variable "image_repo" {
  type = string
}
variable "env" {
  type = string
}

variable service_vars {
  type        = map(any)
  description = "Service vars"
}
variable service_list {
  type        = list(string)
  description = "Service List"
}
