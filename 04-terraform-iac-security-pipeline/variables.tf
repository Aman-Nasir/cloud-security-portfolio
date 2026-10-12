variable "project_name" {
  type    = string
  default = "secure-vpc"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  type    = string
  default = "10.0.1.0/24"
}

variable "private_subnet_cidr" {
  type    = string
  default = "10.0.2.0/24"
}
variable "account_id" {
  type    = string
  default = "123456789012" # placeholder, kabhi asli apply karo to apna account ID do
}