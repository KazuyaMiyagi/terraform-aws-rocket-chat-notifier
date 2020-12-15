module "rocket_chat_notifier" {
  source      = "../../"
  webhook_url = "https://example.com/hooks/xxx/xx"
  channel     = "#notice"
}

resource "aws_codestarnotifications_notification_rule" "codepipeline" {
  detail_type = "BASIC"

  event_type_ids = [
    "codepipeline-pipeline-action-execution-succeeded",
    "codepipeline-pipeline-action-execution-failed",
    "codepipeline-pipeline-action-execution-canceled",
    "codepipeline-pipeline-action-execution-started",
    "codepipeline-pipeline-stage-execution-started",
    "codepipeline-pipeline-stage-execution-succeeded",
    "codepipeline-pipeline-stage-execution-resumed",
    "codepipeline-pipeline-stage-execution-canceled",
    "codepipeline-pipeline-stage-execution-failed",
    "codepipeline-pipeline-pipeline-execution-failed",
    "codepipeline-pipeline-pipeline-execution-canceled",
    "codepipeline-pipeline-pipeline-execution-started",
    "codepipeline-pipeline-pipeline-execution-resumed",
    "codepipeline-pipeline-pipeline-execution-succeeded",
    "codepipeline-pipeline-pipeline-execution-superseded",
    "codepipeline-pipeline-manual-approval-failed",
    "codepipeline-pipeline-manual-approval-needed",
    "codepipeline-pipeline-manual-approval-succeeded",
  ]

  name = "rocketchat-notifier-codepipeline"

  resource = aws_codepipeline.example.arn

  target {
    address = module.rocket_chat_notifier.rocket_chat_notifier_topic_arn
  }
}

resource "aws_codestarnotifications_notification_rule" "codebuild" {
  detail_type = "BASIC"

  event_type_ids = [
    "codebuild-project-build-state-failed",
    "codebuild-project-build-state-succeeded",
    "codebuild-project-build-state-in-progress",
    "codebuild-project-build-state-stopped",
    "codebuild-project-build-phase-failure",
    "codebuild-project-build-phase-success",
  ]

  name = "rocketchat-notifier-codebuild-invalidator"

  resource = aws_codebuild_project.example.arn

  target {
    address = module.rocket_chat_notifier.rocket_chat_notifier_topic_arn
  }
}
