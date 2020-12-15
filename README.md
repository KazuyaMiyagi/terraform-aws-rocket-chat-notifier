Amazon Rocket.Chat notifier Terraform module
====================================================================================================

This terraform module creates an AWS sns topic to notify Rocket.Chat

Usage
----------------------------------------------------------------------------------------------------

```hcl
module "rocket_chat_notifier" {
  source      = "KazuyaMiyagi/rocket-chat-notifier/aws"
  webhook_url = "https://example.com/hooks/xxx/xx"
  channel     = "#notice"
}
```

Examples
----------------------------------------------------------------------------------------------------

* [Simple](https://github.com/KazuyaMiyagi/terraform-aws-rocket-chat-notifier/tree/master/examples/simple)

Requirements
----------------------------------------------------------------------------------------------------

| Name      | Version    |
|-----------|------------|
| terraform | >= 0.12.\* |
| aws       | >= 3.12.\* |

Providers
----------------------------------------------------------------------------------------------------

| Name | Version    |
|------|------------|
| aws  | >= 3.12.\* |

Inputs
----------------------------------------------------------------------------------------------------

| Name         | Description              | Type     | Default | Required |
|--------------|--------------------------|----------|---------|:--------:|
| webhook\_url | Rocket.Chat webhook url  | `string` | `""`    | yes      |
| channel      | Rocket.Chat channel name | `string` | `""`    | yes      |

Outputs
----------------------------------------------------------------------------------------------------

| Name                               | Description                        |
|------------------------------------|------------------------------------|
| rocket\_chat\_notifier\_topic\_arn | rocket-chat-notifier sns topic arn |


License
----------------------------------------------------------------------------------------------------

Apache 2 Licensed. See LICENSE for full details.
