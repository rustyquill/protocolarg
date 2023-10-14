#
# variables for the arg resources
# they need to be added to the terraform cloud workspace!
#

variable "forum_username" {
  type = string
  description = "The username for the forum authentication to view private groups"
  sensitive = true
}

variable "forum_password" {
  type = string
  description = "The password for the forum authentication to view private groups"
  sensitive = true
}

variable "cvs_username" {
  type = string
  description = "The username to access the code challenge cvs repository"
  sensitive = true
}

variable "cvs_password" {
  type = string
  description = "The password to access the code challenge cvs repository"
  sensitive = true
}

