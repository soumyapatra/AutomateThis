data "aws_route53_zone" "selected" {
  name         = "${var.domain_name}"
  private_zone = true
}

resource "aws_route53_record" "cname_record" {
  count   = var.create_record ? 1 : 0
  zone_id = data.aws_route53_zone.selected.zone_id
  name    = var.sub_domain_name
  type    = "CNAME"
  records = ["${var.alias_domain_name}"]
  ttl     = 10
}

resource "aws_route53_zone_association" "secondary" {
  count   = var.associate_vpc ? 1 : 0
  zone_id = data.aws_route53_zone.selected.zone_id
  vpc_id  = "${var.vpc_id}"
  vpc_region = "${var.vpc_region}"
}
