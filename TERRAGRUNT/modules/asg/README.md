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
| [aws_autoscaling_group.asg1](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/autoscaling_group) | resource |
| [aws_iam_instance_profile.worker-node](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_instance_profile) | resource |
| [aws_iam_role.worker-node](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role_policy_attachment.worker-node-AmazonEC2ContainerRegistryReadOnly](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.worker-node-AmazonEKSWorkerNodePolicy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.worker-node-AmazonEKS_CNI_Policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_launch_configuration.lc1](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/launch_configuration) | resource |
| [aws_ami.eks-worker](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/ami) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_ami_name"></a> [ami\_name](#input\_ami\_name) | AMI NAME | `string` | `"amazon-eks-node-1.22-v*"` | no |
| <a name="input_ami_owner_id"></a> [ami\_owner\_id](#input\_ami\_owner\_id) | AMI Owner Acct Id | `string` | `"602401143452"` | no |
| <a name="input_cert_auth_data"></a> [cert\_auth\_data](#input\_cert\_auth\_data) | EKS Auth Cert Data | `string` | n/a | yes |
| <a name="input_desired_asg_size"></a> [desired\_asg\_size](#input\_desired\_asg\_size) | Desired Asg Size | `string` | `"3"` | no |
| <a name="input_eks_cluster_name"></a> [eks\_cluster\_name](#input\_eks\_cluster\_name) | EKS Cluster Name | `string` | n/a | yes |
| <a name="input_eks_endpoint"></a> [eks\_endpoint](#input\_eks\_endpoint) | EKS endpoint for Init script | `string` | n/a | yes |
| <a name="input_eks_version"></a> [eks\_version](#input\_eks\_version) | EKS Version | `string` | `"1.22"` | no |
| <a name="input_instance_type"></a> [instance\_type](#input\_instance\_type) | Instance type | `string` | `"c5a.xlarge"` | no |
| <a name="input_max_asg_size"></a> [max\_asg\_size](#input\_max\_asg\_size) | Maximum Asg Size | `string` | `"6"` | no |
| <a name="input_min_asg_size"></a> [min\_asg\_size](#input\_min\_asg\_size) | Minimum Asg Size | `string` | `"3"` | no |
| <a name="input_name"></a> [name](#input\_name) | SG Name | `string` | n/a | yes |
| <a name="input_subnets"></a> [subnets](#input\_subnets) | ASG Subnets | `list(string)` | n/a | yes |
| <a name="input_use_eks_default_image"></a> [use\_eks\_default\_image](#input\_use\_eks\_default\_image) | Use Amazon default EKS Image | `bool` | `false` | no |
| <a name="input_worker_sg_ids"></a> [worker\_sg\_ids](#input\_worker\_sg\_ids) | worker SG ID's list | `list(string)` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_eks_worker_role_arn"></a> [eks\_worker\_role\_arn](#output\_eks\_worker\_role\_arn) | n/a |
<!-- END_TF_DOCS -->