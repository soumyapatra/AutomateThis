#EKS IAM ROLE

resource "aws_iam_role" "master" {
  name = "${var.name}_master_iam_role"

  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "eks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

resource "aws_iam_role_policy_attachment" "master-AmazonEKSClusterPolicy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = "${aws_iam_role.master.name}"
}

resource "aws_iam_role_policy_attachment" "master-AmazonEKSServicePolicy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSServicePolicy"
  role       = "${aws_iam_role.master.name}"
}

#EKS 

resource "aws_eks_cluster" "master" {
  name            = "${var.name}"
  role_arn        = "${aws_iam_role.master.arn}"
  version = "${var.eks_version}"

  vpc_config {
    security_group_ids = var.sg_id
#    subnet_ids         = ["${aws_subnet.demo.*.id}"]
#    subnet_ids         = ["${join(",", "aws_subnet.demo.*.id")}"]
    subnet_ids         = "${var.subnets}"
    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs = ["3.7.168.159/32", "3.6.98.170/32"]
  }

  depends_on = [
    aws_iam_role_policy_attachment.master-AmazonEKSClusterPolicy,
    aws_iam_role_policy_attachment.master-AmazonEKSServicePolicy,
  ]
}

data "tls_certificate" "example" {
  url = aws_eks_cluster.master.identity[0].oidc[0].issuer
}

resource "aws_iam_openid_connect_provider" "oidc" {
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.example.certificates[0].sha1_fingerprint]
  url             = aws_eks_cluster.master.identity.0.oidc.0.issuer
}

locals {
  oidc = {
    arn = aws_iam_openid_connect_provider.oidc.arn
    url = replace(aws_iam_openid_connect_provider.oidc.url, "https://", "")
    id = split("/",aws_iam_openid_connect_provider.oidc.arn)[3]
  }
}
