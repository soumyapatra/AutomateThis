output "vnet_id" {
  value = azurerm_virtual_network.vnet.id
}

output "subnet_ids" {
  value = { for s in azurerm_subnet.subnets : s.name => s.id }
}

output "private_subnet_address" {
  value = {for s in local.private_subnets : s.name => azurerm_subnet.subnets[s.name].address_prefixes}
}

output "public_subnet_address" {
  value = {for s in local.public_subnets : s.name => azurerm_subnet.subnets[s.name].address_prefixes}
}

output "private_subnet_ids" {
  value = [for name, subnet in azazurerm_subnet.subnets : subnet.id if local.all_subnets[name].type == "private" ]
}