resource "aws_iam_policy" "lb_cont_policy" {
  name = "${var.name}_lb_controller_policy"
  policy = file("./policy.json")
}


resource "aws_iam_role" "lb_cont_role" {
  name = "${var.name}_lb_controller_role"

  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "${var.oidc_arn}"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "${var.oidc_provider}:aud": "sts.amazonaws.com",
                    "${var.oidc_provider}:sub": "system:serviceaccount:kube-system:aws-load-balancer-controller"
                }
            }
        }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "attach1" {
  role       = aws_iam_role.lb_cont_role.name
  policy_arn = aws_iam_policy.lb_cont_policy.arn
}
provider "helm" {
  kubernetes {
    host                   = var.eks_endpoint
    token                  = data.aws_eks_cluster_auth.master.token
    cluster_ca_certificate = base64decode(var.eks_cert_auth_data)
  }
}
provider "kubectl" {
  host                   = var.eks_endpoint
  token                  = data.aws_eks_cluster_auth.master.token
  cluster_ca_certificate = base64decode(var.eks_cert_auth_data)
  load_config_file       = false
}
resource "kubectl_manifest" "lb_controller_sa" {
    yaml_body = templatefile("aws_lb_controller_sa.tfpl", { role_arn = aws_iam_role.lb_cont_role.arn })
}

data "aws_eks_cluster_auth" "master" {
  name = var.eks_name
}

resource "helm_release" "lb" {
  name       = "aws-load-balancer-controller"
  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-load-balancer-controller"
  namespace  = "kube-system"

  set {
    name  = "region"
    value = var.region
  }

  set {
    name  = "vpcId"
    value = var.vpc_id
  }

  set {
    name  = "serviceAccount.create"
    value = "false"
  }

  set {
    name  = "serviceAccount.name"
    value = "aws-load-balancer-controller"
  }

  set {
    name  = "clusterName"
    value = var.eks_name
  }
}
