#############################################
# Deployment
#############################################
variable "initial_deployment" {
  description = "Indicates whether this is the first deployment"
  type        = bool
}

#############################################
# Email
#############################################
variable "email" {
  description = "Email"
  type        = string
}

#############################################
# Domains
#############################################
variable "frontend_domain" {
  description = "Frontend domain"
  type        = string
}

variable "backend_domain" {
  description = "Backend domain"
  type        = string
}

#############################################
# Digital Ocean variables
#############################################
variable "do_token" {
  description = "DigitalOcean API token"
  type        = string
}

variable "do_spaces_access_id" {
  description = "DigitalOcean Spaces access id"
  type        = string
}

variable "do_spaces_secret_key" {
  description = "DigitalOcean Spaces secret key"
  type        = string
}

#############################################
# Cloudflare variables
#############################################
variable "cloudflare_api_token" {
  description = "cloudflare API token"
  type        = string
}

variable "cloudflare_zone_id" {
  description = "cloudflare zone id"
  type        = string
}

#############################################
# Cloudflare variables
#############################################
variable "dockerhub_config" {
  description = "Full path to the dockerhub config file used to download images from private registry"
  type        = string
}

#############################################
# Cluster variables
#############################################
variable cluster_name {
  description = "The name of the kubernetes cluster to create"
  type        = string
}

variable region {
  description = "The digital ocean region slug for where to create resources"
  type        = string
  default     = "ams3"  # Amsterdam
}

variable min_nodes {
  description = "The minimum number of nodes in the default pool"
  type        = number
  default     = 5
}

variable max_nodes {
  description = "The maximum number of nodes in the default pool"
  type        = number
  default     = 10
}

variable default_node_size {
  description = "The default digital ocean node slug for each node in the default pool"
  type        = string
  default     = "s-1vcpu-2gb"
}

#############################################
# Django variables
#############################################
variable django_image {
  description = "The image used for Django and worker deployments"
  type        = string
}

variable django_secret {
  description = "The secret key used for Django and worker deployments"
  type        = string
}
