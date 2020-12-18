from datetime import datetime, timezone, timedelta
import json
import logging
import os
import traceback
import urllib.request

logger = logging.getLogger()

COLORS = {
    "CANCELED": "orange",
    "FAILED": "red",
    "IN_PROGRESS": "black",
    "RESUMED": "orange",
    "START": "black",
    "STARTED": "black",
    "STOPPED": "orange",
    "SUCCEEDED": "green",
    "SUCCESS": "green",
}

ICONS = {
    "sns": "https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v7.0/dist/ApplicationIntegration/SNS.png",
    "codecommit": "https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v7.0/dist/DeveloperTools/CodeCommit.png",
    "codebuild": "https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v7.0/dist/DeveloperTools/CodeBuild.png",
    "codedeploy": "https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v7.0/dist/DeveloperTools/CodeDeploy.png",
    "codepipeline": "https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v7.0/dist/DeveloperTools/CodePipeline.png",
    "user": "https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v7.0/dist/General/User.png",
}


def subscribe_template(sns):
    subscribe_link = "[Link](%s)" % (sns.get("SubscribeURL"))
    return {
        "avatar": ICONS.get("sns"),
        "text": sns.get("Message"),
        "attachments": [
            {
                "title": "Detail",
                "fields": [
                    {"short": True, "title": "Subscribe url", "value": subscribe_link},
                ],
            },
        ],
    }


def codecommit_template(sns):
    message = json.loads(sns.get("Message"))
    detail = message.get("detail")
    repository = detail.get("repositoryName") or ", ".join(detail.get("repositoryNames"))

    fields = [
        {"short": True, "title": "Event", "value": detail.get("event")},
        {"short": True, "title": "Repository Name", "value": repository},
    ]

    if detail.get("title") is not None:
        fields.append({"short": True, "title": "Title", "value": detail.get("title")})

    if detail.get("author") is not None:
        fields.append({"short": True, "title": "Author", "value": detail.get("author")})

    if detail.get("notificationBody") is not None:
        fields.append({"short": False, "title": "Notification body", "value": detail.get("notificationBody")})

    return {
        "avatar": ICONS.get("codecommit"),
        "text": message.get("detailType"),
        "attachments": [
            {
                "title": "Detail",
                "fields": fields,
            },
        ],
    }


def codebuild_template(sns):
    message = json.loads(sns.get("Message"))
    detail = message.get("detail")
    additional_information = detail.get("additional-information")
    return {
        "avatar": ICONS.get("codebuild"),
        "text": message.get("detailType"),
        "attachments": [
            {
                "title": "Detail",
                "color": COLORS.get(detail.get("build-status")),
                "fields": [
                    {"short": True, "title": "Project name", "value": detail.get("project-name")},
                    {"short": True, "title": "Build status", "value": detail.get("build-status")},
                    {"short": True, "title": "Current phase", "value": detail.get("current-phase")},
                    {"short": True, "title": "Initiator", "value": additional_information.get("initiator")},
                    {"short": True, "title": "Version", "value": detail.get("version")},
                ],
            },
        ],
    }


def codedeploy_template(sns):
    message = json.loads(sns.get("Message"))
    detail = message.get("detail")
    print(detail.keys())
    return {
        "avatar": ICONS.get("codedeploy"),
        "text": message.get("detailType"),
        "attachments": [
            {
                "title": "Detail",
                "color": COLORS.get(detail.get("state")),
                "fields": [
                    {"short": True, "title": "Application", "value": detail.get("application")},
                    {"short": True, "title": "Deployment id", "value": detail.get("deploymentId")},
                    {"short": True, "title": "Deployment group", "value": detail.get("deploymentGroup")},
                    {"short": True, "title": "Instance gropu id", "value": detail.get("instanceGroupId")},
                    {"short": True, "title": "State", "value": detail.get("state")},
                    {"short": True, "title": "Region", "value": detail.get("region")},
                ],
            },
        ],
    }


def codepipeline_template(sns):
    message = json.loads(sns.get("Message"))
    detail = message.get("detail")
    fields = [
        {"short": True, "title": "Pipeline", "value": detail.get("pipeline")},
        {"short": True, "title": "State", "value": detail.get("state")},
        {"short": True, "title": "Version", "value": detail.get("version")},
    ]

    if detail.get("action") is not None:
        fields.append({"short": True, "title": "Action", "value": detail.get("action")})

    if detail.get("stage") is not None:
        fields.append({"short": True, "title": "Stage", "value": detail.get("stage")})

    return {
        "avatar": ICONS.get("codepipeline"),
        "text": message.get("detailType"),
        "attachments": [
            {
                "title": "Detail",
                "color": COLORS.get(detail.get("state")),
                "fields": fields,
            },
        ],
    }


def approve_template(sns):
    message = json.loads(sns.get("Message"))
    approval = message.get("approval")

    jst = timezone(timedelta(hours=+9), 'JST')
    expire = message.get('approval', {}).get('expires')
    expire_jst = str(datetime.strptime(expire, '%Y-%m-%dT%H:%M%z').astimezone(jst))

    if approval.get("externalEntityLink") is None:
        external_link = None
    else:
        external_link = "[Link](%s)" % (approval.get("externalEntityLink"))

    approve_link = "[Link](%s)" % (approval.get("approvalReviewLink"))

    return {
        "avatar": ICONS.get("user"),
        "text": sns.get("Subject"),
        "attachments": [
            {
                "title": "Detail",
                "fields": [
                    {"short": True, "title": "Pipeline name",        "value": approval.get("piplineName")},
                    {"short": True, "title": "Stage name",           "value": approval.get("stageName")},
                    {"short": True, "title": "Action name",          "value": approval.get("actionName")},
                    {"short": True, "title": "Expires",              "value": expire_jst},
                    {"short": True, "title": "External entity link", "value": external_link},
                    {"short": True, "title": "Approval review link", "value": approve_link},
                 ],
            },
        ],
    }


def lambda_handler(event, context):
    try:
        for record in event.get("Records"):
            body = {
                "channel": os.environ.get('CHANNEL'),
                "alias": "AWS Notification",
            }

            sns = record.get("Sns")

            # AWS SNS Subscribe
            if sns.get("Type") == "SubscriptionConfirmation":
                body.update(subscribe_template(sns))

            elif sns.get("Type") == "Notification":

                # AWS CodePipeline approve action
                if "Subject" in sns:
                    body.update(approve_template(sns))

                else:
                    source = json.loads(sns.get("Message")).get("source")

                    # AWS CodeCommit
                    if source == "aws.codecommit":
                        body.update(codecommit_template(sns))

                    # AWS CodeBuild
                    elif source == "aws.codebuild":
                        body.update(codebuild_template(sns))

                    # AWS CodeDeploy
                    elif source == "aws.codedeploy":
                        body.update(codedeploy_template(sns))

                    # AWS CodePipeline
                    elif source == "aws.codepipeline":
                        body.update(codepipeline_template(sns))

                    else:
                        raise ValueError("Unknown message type.", sns)
            else:
                raise ValueError("Unknown message type.", sns)

            url = os.environ.get('WEBHOOK_URL')

            header = {
                'Content-Type': 'application/json'
            }

            req = urllib.request.Request(url, json.dumps(body).encode(), header)
            urllib.request.urlopen(req)

    except ValueError:
        raise
    except Exception:
        logger.error({"event": event, "traceback": traceback.format_exc()})
