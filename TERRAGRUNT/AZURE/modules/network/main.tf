

module rg {
  source = "../rg"
  resource_group_name = var.rg_name
  region_code =  var.location
}

module "vnet" {
    source = "../vnet"
    resource_group_name = module.rg.resource_group_name
    location = module.rg.resource_group_location
    vnet_name = var.vnet_name
    vnet_cidr = var.network_cidr
}