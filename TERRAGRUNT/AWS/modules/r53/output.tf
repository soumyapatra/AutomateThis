output "sub_domain_name" {
  value = length(aws_route53_record.cname_record) > 0 ? aws_route53_record.cname_record[0].name : ""
}
