<!-- BEGIN_TF_DOCS -->




[36mprovider.aws[0m




[36mresource.aws_route53_record.cname_record (resource)[0m (https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route53_record)
[36mresource.aws_route53_zone_association.secondary (resource)[0m (https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route53_zone_association)
[36mdata.aws_route53_zone.selected (data source)[0m (https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/route53_zone)


[36minput.alias_domain_name[0m (required)
[90mCNAME to set as record[0m

[36minput.domain_name[0m (required)
[90mHost Zone Name[0m

[36minput.sub_domain_name[0m (required)
[90msub-domain name used for CNAME[0m

[36minput.vpc_id[0m (required)
[90mVPC ID that needed to ne associated with r53[0m

[36minput.vpc_region[0m (required)
[90mVPC region[0m


[36moutput.sub_domain_name[0m
[90mn/a[0m
<!-- END_TF_DOCS -->