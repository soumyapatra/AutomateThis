output "rg_name" {
  value = module.rg.resource_group_name
}

output "location" {
  value = module.rg.resource_group_location
}

output "private_subnet_ids" {
  value = module.vnet.private_subnet_ids
}