variable "aws_access_key"{}
variable "aws_secret_key"{}
variable "ami_id" {}
variable "instance_type" {}

variable "root_vl_type" {}
variable "root_vl_size" {}
variable "subnet_id" {}
variable "number_of_instances" {}
variable "sgs" {}
variable "user_data" {}
variable "tag_name" {}
variable "key_name" {}
variable "region" {}
variable "tags" {
  default = {}
}


provider "aws" {
        access_key              =   "${var.aws_access_key}"
        secret_key              =   "${var.aws_secret_key}"
        region                  =   "${var.region}"
}
resource "aws_instance" "my-instance" {
        ami                     =   "${var.ami_id}"
        instance_type           =   "${var.instance_type}"
        subnet_id               =   "${var.subnet_id}"
        user_data               =   "${file(var.user_data)}"
        root_block_device {
                volume_type     =   "${var.root_vl_type}"
                volume_size     =   "${var.root_vl_size}"
        }
        tags                    =   "${var.tags}"
        vpc_security_group_ids  =   "${var.sgs}"
        key_name                =   "${var.key_name}"
}
