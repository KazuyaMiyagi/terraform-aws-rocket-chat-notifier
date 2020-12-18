data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

resource "random_id" "main" {
  byte_length = 10
}
