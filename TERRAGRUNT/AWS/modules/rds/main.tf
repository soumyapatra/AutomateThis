data "aws_db_snapshot" "db_snapshot" {
    most_recent = true
    db_instance_identifier = "${var.db_instance_identifier}"
}

resource "aws_db_instance" "db" {
  instance_class       = "${var.instance_type}"
  db_subnet_group_name = "${var.db_subnet_group}"
  snapshot_identifier  = "${data.aws_db_snapshot.db_snapshot.id}"
  vpc_security_group_ids = ["${var.db_sg_id}"]
  skip_final_snapshot = true
  storage_encrypted = true
}

module "route53" {
  source = "../r53"
  create_record = true
  sub_domain_name = var.sub_domain_name
  alias_domain_name = aws_db_instance.db.address
  domain_name = var.domain_name
}
