resource "aws_sns_topic" "main" {
  name = "rocket-chat-notifier"
}

data "aws_iam_policy_document" "main" {
  statement {
    actions = ["sns:Publish"]

    principals {
      type = "Service"
      identifiers = [
        "codestar-notifications.amazonaws.com",
        "ses.amazonaws.com",
      ]
    }

    resources = [aws_sns_topic.main.arn]
  }
}

resource "aws_sns_topic_policy" "main" {
  arn    = aws_sns_topic.main.arn
  policy = data.aws_iam_policy_document.main.json
}


resource "aws_sns_topic_subscription" "main" {
  topic_arn = aws_sns_topic.main.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.main.arn
}

