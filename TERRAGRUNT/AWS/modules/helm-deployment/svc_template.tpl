replicaCount: ${replica_count}
image:
  repository: "${image_repo}"
  name: "${image_name}"
  tag: "${image_tag}"
  pullPolicy: Always
service:
  name: urlshortener
  type: NodePort
  port: ${service_port}
  targetPort: ${target_port}
env:
  name: ${env}
