#Master SG
locals {
  prod_sg = var.prod_sg
}

resource "aws_security_group" "master" {
  name        = "${var.name}-cluster"
  description = "Cluster communication with worker nodes"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = var.name
  }
}

# OPTIONAL: Allow inbound traffic from your local workstation external IP
#           to the Kubernetes. You will need to replace A.B.C.D below with
#           your real IP. Services like icanhazip.com can help you find this.
resource "aws_security_group_rule" "master-ingress-workstation-https" {
  cidr_blocks       = var.bastion_public_ip_list
  description       = "Allow workstation to communicate with the cluster API Server"
  from_port         = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.master.id
  to_port           = 443
  type              = "ingress"
}

resource "aws_security_group_rule" "master-ingress-node-https" {
  description              = "Allow pods to communicate with the cluster API Server"
  from_port                = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.master.id
  source_security_group_id = aws_security_group.worker.id
  to_port                  = 443
  type                     = "ingress"
}

resource "aws_security_group_rule" "master-ingress-bastion-https" {
  description              = "Allow pods to communicate with the cluster API Server"
  from_port                = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.master.id
  source_security_group_id = var.bastion_sg_id
  to_port                  = 443
  type                     = "ingress"
}

resource "aws_security_group_rule" "master-ingress-vpc-https" {
  count = local.prod_sg ? 1 : 0
  description              = "Allow bastion sg id to connect to EKS Api server if in same VPC"
  from_port                = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.master.id
  source_security_group_id = var.prod_sg_id
  to_port                  = 443
  type                     = "ingress"
}


#Worker SG

resource "aws_security_group" "worker" {
  name        = "${var.name}-node"
  description = "Security group for all nodes in the cluster"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = "${
    tomap({
        "Name" = "${var.name}"
        "kubernetes.io/cluster/${var.name}" = "shared"
    })
  }"
}

resource "aws_security_group_rule" "worker-ingress-self" {
  description              = "Allow node to communicate with each other"
  from_port                = 0
  protocol                 = "-1"
  security_group_id        = "${aws_security_group.worker.id}"
  source_security_group_id = "${aws_security_group.worker.id}"
  to_port                  = 65535
  type                     = "ingress"
}

resource "aws_security_group_rule" "worker-ingress-cluster-https" {
  description              = "Allow worker Kubelets and pods to receive communication from the cluster control plane"
  from_port                = 443
  protocol                 = "tcp"
  security_group_id        = "${aws_security_group.worker.id}"
  source_security_group_id = "${aws_security_group.master.id}"
  to_port                  = 443
  type                     = "ingress"
}

resource "aws_security_group_rule" "worker-ingress-cluster-others" {
  description              = "Allow worker Kubelets and pods to receive communication from the cluster control plane"
  from_port                = 1025
  protocol                 = "tcp"
  security_group_id        = "${aws_security_group.worker.id}"
  source_security_group_id = "${aws_security_group.master.id}"
  to_port                  = 65535
  type                     = "ingress"
}

resource "aws_security_group_rule" "worker-ingress-bastion" {
  description              = "Allow worker Kubelets and pods to receive communication from bastion"
  from_port                = 0
  protocol                 = "tcp"
  security_group_id        = "${aws_security_group.worker.id}"
  source_security_group_id = var.bastion_sg_id
  to_port                  = 65535
  type                     = "ingress"
}

#DB Security Group

resource "aws_security_group" "rds" {
  name        = "${var.name}-rds"
  description = "Security group for all Dbs in the cluster"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = "${
    tomap({
        "Name" = "${var.name}"
        "kubernetes.io/cluster/${var.name}" = "shared"
    })
  }"
}


resource "aws_security_group_rule" "rds-mysql-worker" {
  description              = "Allow worker node access to MYSQL RDS"
  from_port                = 3306
  protocol                 = "tcp"
  security_group_id        = "${aws_security_group.rds.id}"
  source_security_group_id = "${aws_security_group.worker.id}"
  to_port                  = 3306
  type                     = "ingress"
}

resource "aws_security_group_rule" "rds-mysql-bastion" {
  description              = "Allow bastion access to MYSQL RDS"
  from_port                = 3306
  protocol                 = "tcp"
  security_group_id        = "${aws_security_group.rds.id}"
  source_security_group_id = var.bastion_sg_id
  to_port                  = 3306
  type                     = "ingress"
}

#resource "aws_security_group_rule" "rds-mysql-bastion" {
#  description              = "Allow EKS Cluster access to MYSQL RDS"
#  from_port                = 3306
#  protocol                 = "tcp"
#  security_group_id        = "${aws_security_group.rds.id}"
#  source_security_group_id = var.eks_sg_id
#  to_port                  = 3306
#  type                     = "ingress"
#}
