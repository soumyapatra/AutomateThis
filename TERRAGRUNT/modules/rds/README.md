<!-- BEGIN_TF_DOCS -->
## Requirements

No requirements.

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | n/a |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_db_instance.db](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/db_instance) | resource |
| [aws_db_snapshot.db_snapshot](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/db_snapshot) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_db_instance_identifier"></a> [db\_instance\_identifier](#input\_db\_instance\_identifier) | RDS Instance Identifier for Picking up Snaphots | `string` | n/a | yes |
| <a name="input_db_sg_id"></a> [db\_sg\_id](#input\_db\_sg\_id) | RDS Security Group | `string` | n/a | yes |
| <a name="input_db_subnet_group"></a> [db\_subnet\_group](#input\_db\_subnet\_group) | RDS Subnet Group | `string` | n/a | yes |
| <a name="input_instance_type"></a> [instance\_type](#input\_instance\_type) | RDS Instance type | `string` | `"db.m5.xlarge"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_db_instance_arn"></a> [db\_instance\_arn](#output\_db\_instance\_arn) | n/a |
| <a name="output_rds_dns_name"></a> [rds\_dns\_name](#output\_rds\_dns\_name) | n/a |
| <a name="output_rds_id"></a> [rds\_id](#output\_rds\_id) | n/a |
<!-- END_TF_DOCS -->