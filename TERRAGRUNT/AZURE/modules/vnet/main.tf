############################
# Locals
############################
locals {
  public_subnets = [
    for i, cidr in var.public_subnet_cidrs : {
      name           = "public-subnet-${i + 1}"
      address_prefix = cidr
      type           = "public"
    }
  ]

  private_subnets = [
    for i, cidr in var.private_subnet_cidrs : {
      name           = "private-subnet-${i + 1}"
      address_prefix = cidr
      type           = "private"
    }
  ]

  all_subnets = concat(local.public_subnets, local.private_subnets)
}

############################
# VNet
############################
resource "azurerm_virtual_network" "vnet" {
  name                = var.vnet_name
  resource_group_name = var.resource_group_name
  location            = var.location
  address_space       = var.address_space
}

############################
# Subnets
############################
resource "azurerm_subnet" "subnets" {
  for_each = { for subnet in local.all_subnets : subnet.name => subnet }

  name                 = each.value.name
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [each.value.address_prefix]
}

############################
# Public IP for NAT Gateway
############################
resource "azurerm_public_ip" "nat_gw_ip" {
  name                = "${var.vnet_name}-nat-ip"
  location            = var.location
  resource_group_name = var.resource_group_name
  allocation_method   = "Static"
  sku                 = "Standard"
}

############################
# NAT Gateway
############################
resource "azurerm_nat_gateway" "nat_gw" {
  name                = "${var.vnet_name}-nat-gw"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku_name            = "Standard"
}

resource "azurerm_nat_gateway_public_ip_association" "nat_gw_assoc" {
  nat_gateway_id       = azurerm_nat_gateway.nat_gw.id
  public_ip_address_id = azurerm_public_ip.nat_gw_ip.id
}

############################
# Associate NAT GW with Private Subnets
############################
resource "azurerm_subnet_nat_gateway_association" "private_assoc" {
  for_each      = { for subnet in local.private_subnets : subnet.name => subnet }
  subnet_id     = azurerm_subnet.subnets[each.key].id
  nat_gateway_id = azurerm_nat_gateway.nat_gw.id
}

############################
# Route Table for Public Subnets
############################
resource "azurerm_route_table" "public_rt" {
  name                = "${var.vnet_name}-public-rt"
  location            = var.location
  resource_group_name = var.resource_group_name
}

resource "azurerm_route" "internet_route" {
  name                   = "default-internet"
  resource_group_name    = var.resource_group_name
  route_table_name       = azurerm_route_table.public_rt.name
  address_prefix         = "0.0.0.0/0"
  next_hop_type          = "Internet"
}

resource "azurerm_subnet_route_table_association" "public_assoc" {
  for_each        = { for subnet in local.public_subnets : subnet.name => subnet }
  subnet_id       = azurerm_subnet.subnets[each.key].id
  route_table_id  = azurerm_route_table.public_rt.id
}