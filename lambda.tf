data "archive_file" "main" {
  type        = "zip"
  source_file = "${path.module}/app.py"
  output_path = "${path.module}/app.py.zip"
}

resource "aws_lambda_function" "main" {
  function_name    = "RocketChatNotifier"
  filename         = data.archive_file.main.output_path
  role             = aws_iam_role.lambda.arn
  handler          = "app.lambda_handler"
  source_code_hash = data.archive_file.main.output_base64sha256
  runtime          = "python3.8"

  environment {
    variables = {
      WEBHOOK_URL = var.webhook_url
      CHANNEL     = var.channel
    }
  }
}

resource "aws_lambda_permission" "main" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.main.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.main.arn
}
