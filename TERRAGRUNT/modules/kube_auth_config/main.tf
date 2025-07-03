data "aws_eks_cluster_auth" "master" {
  name = var.eks_name
}

#Kubernetes Auth Config Setup
provider "kubernetes" {
  host                   = var.eks_endpoint
  token                  = data.aws_eks_cluster_auth.master.token
  cluster_ca_certificate = base64decode(var.eks_cert_auth_data)
}

#resource "kubernetes_config_map" "aws-auth" {
#  metadata {
#    name      = "aws-auth"
#    namespace = "kube-system"
#  }
#
#  data = {
#    mapRoles = yamlencode(
#      [{
#        rolearn  = "${var.bastion_role_arn}"
#        username = "${var.bastion_role_name}"
#        groups   = ["system:masters"]
#      }]
#    )
#  }
#}

#------------ROLE CREATION AND ATTACHMENT--------------#
resource "aws_iam_role" "eks_nodes" {
  name = "${var.ng_name}-worker-role"

  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}


resource "aws_iam_role_policy" "autoscaling-policy" {
  name = "${var.ng_name}-worker-autoscaling-policy"
  role = aws_iam_role.eks_nodes.id

  policy = <<EOF
{
    "Version": "2012-10-17",
          "Statement": [
    { "Effect": "Allow",
      "Action": [
        "autoscaling:DescribeAutoScalingGroups",
        "autoscaling:DescribeAutoScalingInstances",
        "autoscaling:SetDesiredCapacity",
        "autoscaling:TerminateInstanceInAutoScalingGroup"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_policy" "ecr-policy" {
  name        = "${var.ng_name}-worker-ecr-policy"
  path        = "/"
  description = "EKS worker node ECR policy"
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:BatchCheckLayerAvailability",
                "ecr:BatchGetImage",
                "ecr:GetDownloadUrlForLayer",
                "ecr:GetAuthorizationToken"
            ],
            "Resource": "*"
        }
    ]
  })
}

resource "aws_iam_policy" "eks-policy1" {
  name        = "${var.ng_name}-worker-eks-policy1"
  path        = "/"
  description = "EKS worker node ECR policy"
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "sqs:StartMessageMoveTask",
                "sqs:DeleteMessage",
                "ses:ListReceiptFilters",
                "s3:DeleteAccessPoint",
                "ses:GetIdentityMailFromDomainAttributes",
                "cloudfront:CreateInvalidation",
                "ses:ListContactLists",
                "ses:GetEmailIdentity",
                "ses:SendEmail",
                "ses:SendTemplatedEmail",
                "ses:UntagResource",
                "ses:GetIdentityDkimAttributes",
                "s3:DeleteJobTagging",
                "ses:TagResource",
                "ses:DescribeReceiptRuleSet",
                "cloudfront:CopyDistribution",
                "elasticfilesystem:ClientMount",
                "s3:PutLifecycleConfiguration",
                "s3:PutObjectTagging",
                "ec2:UnassignPrivateIpAddresses",
                "ses:BatchGetMetricData",
                "s3:DeleteObject",
                "s3:CreateMultiRegionAccessPoint",
                "ses:ListDeliverabilityTestReports",
                "ses:GetSuppressedDestination",
                "s3:PutAccessPointPolicyForObjectLambda",
                "s3:PutAccountPublicAccessBlock",
                "s3:PutMultiRegionAccessPointPolicy",
                "s3:DeleteStorageLensConfigurationTagging",
                "ec2:ModifyNetworkInterfaceAttribute",
                "ecr:PutImageScanningConfiguration",
                "sqs:SendMessage",
                "s3:PutReplicationConfiguration",
                "s3:DeleteObjectVersionTagging",
                "ec2:AssignPrivateIpAddresses",
                "s3:PutObject",
                "s3:PutBucketNotification",
                "sqs:PurgeQueue",
                "s3:PutObjectVersionAcl",
                "s3:PutAccessPointPublicAccessBlock",
                "ses:SendBulkTemplatedEmail",
                "ses:ListVerifiedEmailAddresses",
                "s3:PutBucketObjectLockConfiguration",
                "s3:CreateJob",
                "s3:PutAccessPointPolicy",
                "ses:GetDeliverabilityTestReport",
                "ecr:InitiateLayerUpload",
                "ecr:PutImageTagMutability",
                "sqs:CancelMessageMoveTask",
                "ses:GetIdentityPolicies",
                "s3:ReplicateTags",
                "ses:GetDomainDeliverabilityCampaign",
                "ses:VerifyDomainIdentity",
                "ses:ListDedicatedIpPools",
                "ses:ListEmailIdentities",
                "ses:ListContacts",
                "ses:GetContactList",
                "s3:AbortMultipartUpload",
                "eks:AssociateEncryptionConfig",
                "s3:PutBucketTagging",
                "s3:UpdateJobPriority",
                "ses:GetConfigurationSet",
                "ses:GetDedicatedIpPool",
                "ses:ListIdentities",
                "s3:PutBucketVersioning",
                "ses:VerifyEmailAddress",
                "ecr:PutLifecyclePolicy",
                "eks:UntagResource",
                "s3:PutIntelligentTieringConfiguration",
                "ses:SendRawEmail",
                "ses:GetSendStatistics",
                "s3:PutMetricsConfiguration",
                "s3:PutStorageLensConfigurationTagging",
                "s3:PutObjectVersionTagging",
                "ses:SendBounce",
                "ses:GetIdentityNotificationAttributes",
                "ecr:PutRegistryScanningConfiguration",
                "ses:ListIdentityPolicies",
                "s3:PutInventoryConfiguration",
                "ses:DescribeActiveReceiptRuleSet",
                "ses:GetAccountSendingEnabled",
                "sqs:TagQueue",
                "s3:PutBucketWebsite",
                "s3:PutBucketRequestPayment",
                "ses:ListImportJobs",
                "s3:PutObjectRetention",
                "ses:ListSuppressedDestinations",
                "s3:CreateAccessPointForObjectLambda",
                "eks:TagResource",
                "ecr:PutReplicationConfiguration",
                "ses:GetExportJob",
                "ses:ListRecommendations",
                "ses:VerifyEmailIdentity",
                "ses:GetContact",
                "s3:PutAnalyticsConfiguration",
                "sqs:UntagQueue",
                "s3:PutAccessPointConfigurationForObjectLambda",
                "ses:GetImportJob",
                "s3:PutStorageLensConfiguration",
                "ses:UpdateAccountSendingEnabled",
                "s3:ReplicateObject",
                "logs:CreateLogStream",
                "ses:SendCustomVerificationEmail",
                "s3:PutBucketAcl",
                "ses:ListReceiptRuleSets",
                "ses:GetTemplate",
                "ses:GetDedicatedIps",
                "s3:DeleteObjectTagging",
                "ses:GetMessageInsights",
                "ses:CreateTemplate",
                "ses:GetIdentityVerificationAttributes",
                "s3:PutObjectLegalHold",
                "s3:PutBucketCORS",
                "ses:GetConfigurationSetEventDestinations",
                "ses:DescribeReceiptRule",
                "ecr:PutImage",
                "ses:GetAccount",
                "ses:GetBlacklistReports",
                "s3:PutBucketLogging",
                "sqs:DeleteQueue",
                "ses:GetEmailTemplate",
                "ses:ListTemplates",
                "ses:GetDeliverabilityDashboardOptions",
                "ses:ListCustomVerificationEmailTemplates",
                "s3:PutAccelerateConfiguration",
                "s3:SubmitMultiRegionAccessPointRoutes",
                "ses:GetSendQuota",
                "ses:DescribeConfigurationSet",
                "s3:RestoreObject",
                "ses:VerifyDomainDkim",
                "ecr:UploadLayerPart",
                "ses:ListTagsForResource",
                "ecr:PutRegistryPolicy",
                "s3:PutEncryptionConfiguration",
                "ses:ListDomainDeliverabilityCampaigns",
                "ses:ListExportJobs",
                "ecr:CompleteLayerUpload",
                "s3:PutObjectAcl",
                "ses:GetCustomVerificationEmailTemplate",
                "s3:PutBucketPublicAccessBlock",
                "s3:PutBucketOwnershipControls",
                "s3:PutJobTagging",
                "s3:UpdateJobStatus",
                "s3:BypassGovernanceRetention",
                "ses:ListEmailTemplates",
                "ses:GetDedicatedIp",
                "s3:PutBucketPolicy",
                "ses:GetEmailIdentityPolicies",
                "sqs:CreateQueue",
                "ses:GetDomainStatisticsReport",
                "eks:AssociateIdentityProviderConfig",
                "ses:SendBulkEmail"
            ],
            "Resource": "*"
        }
    ]
  })
}

resource "aws_iam_policy" "eks-policy2" {
  name        = "${var.ng_name}-worker-eks-policy2"
  path        = "/"
  description = "EKS worker node ECR policy"
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "ssm:CancelCommand",
                "elasticloadbalancing:ModifyListener",
                "elasticloadbalancing:DetachLoadBalancerFromSubnets",
                "elasticloadbalancing:RegisterTargets",
                "elasticloadbalancing:DescribeLoadBalancerPolicyTypes",
                "elasticloadbalancing:CreateLBCookieStickinessPolicy",
                "ssm:CreateActivation",
                "elasticloadbalancing:SetIpAddressType",
                "elasticloadbalancing:DeleteLoadBalancer",
                "ssm:UpdateInstanceInformation",
                "ssm:RemoveTagsFromResource",
                "ssm:AddTagsToResource",
                "elasticloadbalancing:DescribeLoadBalancerPolicies",
                "elasticloadbalancing:CreateRule",
                "elasticloadbalancing:AddListenerCertificates",
                "elasticloadbalancing:DescribeInstanceHealth",
                "elasticloadbalancing:ModifyTargetGroupAttributes",
                "elasticloadbalancing:DeregisterInstancesFromLoadBalancer",
                "elasticloadbalancing:RegisterInstancesWithLoadBalancer",
                "ssm:PutComplianceItems",
                "elasticloadbalancing:CreateTargetGroup",
                "ec2messages:AcknowledgeMessage",
                "elasticloadbalancing:DeregisterTargets",
                "ssm:PutParameter",
                "sts:AssumeRole",
                "elasticloadbalancing:DescribeTargetGroupAttributes",
                "elasticloadbalancing:ModifyRule",
                "ssm:CancelMaintenanceWindowExecution",
                "elasticloadbalancing:DescribeAccountLimits",
                "elasticloadbalancing:AddTags",
                "elasticloadbalancing:DeleteLoadBalancerListeners",
                "ec2messages:SendReply",
                "elasticloadbalancing:DescribeRules",
                "elasticloadbalancing:ModifyLoadBalancerAttributes",
                "kms:UntagResource",
                "sts:TagSession",
                "elasticloadbalancing:ConfigureHealthCheck",
                "kms:GenerateDataKeyWithoutPlaintext",
                "ssmmessages:OpenControlChannel",
                "elasticloadbalancing:SetRulePriorities",
                "elasticloadbalancing:RemoveListenerCertificates",
                "elasticloadbalancing:SetLoadBalancerListenerSSLCertificate",
                "elasticloadbalancing:RemoveTags",
                "ec2messages:DeleteMessage",
                "kms:TagResource",
                "elasticloadbalancing:CreateListener",
                "elasticloadbalancing:DescribeListeners",
                "ssmmessages:OpenDataChannel",
                "sts:DecodeAuthorizationMessage",
                "elasticloadbalancing:CreateAppCookieStickinessPolicy",
                "elasticloadbalancing:ApplySecurityGroupsToLoadBalancer",
                "elasticloadbalancing:DescribeListenerCertificates",
                "sts:AssumeRoleWithWebIdentity",
                "kms:CreateGrant",
                "elasticloadbalancing:CreateLoadBalancerPolicy",
                "elasticloadbalancing:DeleteRule",
                "elasticloadbalancing:DescribeSSLPolicies",
                "elasticloadbalancing:CreateLoadBalancer",
                "elasticloadbalancing:AttachLoadBalancerToSubnets",
                "ssmmessages:CreateControlChannel",
                "elasticloadbalancing:DeleteTargetGroup",
                "elasticloadbalancing:CreateLoadBalancerListeners",
                "ssmmessages:CreateDataChannel",
                "ssm:PutInventory",
                "elasticloadbalancing:SetLoadBalancerPoliciesOfListener",
                "elasticloadbalancing:EnableAvailabilityZonesForLoadBalancer",
                "elasticloadbalancing:DescribeTargetHealth",
                "elasticloadbalancing:DescribeTargetGroups",
                "elasticloadbalancing:ModifyTargetGroup",
                "elasticloadbalancing:DeleteListener"
            ],
            "Resource": "*"
        }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "AmazonEKSWorkerNodePolicy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_nodes.name
}

resource "aws_iam_role_policy_attachment" "AmazonEKS_CNI_Policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_nodes.name
}

resource "aws_iam_role_policy_attachment" "AmazonEC2ContainerRegistryReadOnly" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.eks_nodes.name
}

resource "aws_iam_role_policy_attachment" "ecr-role"{
  policy_arn = aws_iam_policy.ecr-policy.arn
  role       = aws_iam_role.eks_nodes.name
}

resource "aws_iam_role_policy_attachment" "eks-policy1"{
  policy_arn = aws_iam_policy.eks-policy1.arn
  role       = aws_iam_role.eks_nodes.name
}

resource "aws_iam_role_policy_attachment" "eks-policy2"{
  policy_arn = aws_iam_policy.eks-policy2.arn
  role       = aws_iam_role.eks_nodes.name
}

resource "aws_iam_role_policy_attachment" "ssm-role"{
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  role       = aws_iam_role.eks_nodes.name
}

resource "aws_iam_role_policy_attachment" "cwagent-role"{
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
  role       = aws_iam_role.eks_nodes.name
}

resource "aws_iam_role_policy_attachment" "aws-ro"{
  policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
  role       = aws_iam_role.eks_nodes.name
}



resource "kubernetes_config_map" "aws-auth" {
  metadata {
    name      = "aws-auth"
    namespace = "kube-system"
  }

  data = {
    mapRoles = yamlencode(
      [{
        rolearn  = aws_iam_role.eks_nodes.arn
        username = "system:node:{{EC2PrivateDNSName}}"
        groups   = ["system:bootstrappers", "system:nodes"]
      },
      {
        rolearn  = "${var.bastion_role_arn}"
        username = "${var.bastion_role_name}"
        groups   = ["system:masters"]
      }
      ]
    )
  }
}
