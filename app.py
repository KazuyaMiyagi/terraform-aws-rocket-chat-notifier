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
    "STARTED": "black",
    "STOPPED": "orange",
    "SUCCEEDED": "green",
}

ICONS = {
    "sns": "https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/main/dist/ApplicationIntegration/SNS.png",
    "codepipeline": "https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/main/dist/DeveloperTools/CodePipeline.png",
    "codebuild": "https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/main/dist/DeveloperTools/CodeBuild.png",
    "user": "https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/main/dist/General/User.png",
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


def codepipeline_template(sns):
    message = json.loads(sns.get("Message"))
    detail = message.get("detail")
    return {
        "avatar": ICONS.get("codepipeline"),
        "text": message.get("detailType"),
        "attachments": [
            {
                "title": "Detail",
                "color": COLORS.get(detail.get("state")),
                "fields": [
                    {"short": True, "title": "Pipeline", "value": detail.get("pipeline")},
                    {"short": True, "title": "Stage",    "value": detail.get("stage")},
                    {"short": True, "title": "Action",   "value": detail.get("action")},
                    {"short": True, "title": "State",    "value": detail.get("state")},
                    {"short": True, "title": "Version",  "value": detail.get("version")},
                ],
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
                    {"short": True, "title": "Project name",  "value": detail.get("project-name")},
                    {"short": True, "title": "Build status",  "value": detail.get("build-status")},
                    {"short": True, "title": "Current phase", "value": detail.get("current-phase")},
                    {"short": True, "title": "Initiator",     "value": additional_information.get("initiator")},
                    {"short": True, "title": "Version",       "value": detail.get("version")},
                ],
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
            sns = record.get("Sns")

            # AWS SNS Subscribe
            if sns.get("Type") == "SubscriptionConfirmation":
                body = subscribe_template(sns)

            elif sns.get("Type") == "Notification":

                if sns.get("Subject") is None:

                    source = json.loads(sns.get("Message")).get("source")

                    # AWS CodePipeline
                    if source == "aws.codepipeline":
                        body = codepipeline_template(sns)

                    # AWS CodeBuild
                    elif source == "aws.codebuild":
                        body = codebuild_template(sns)

                # AWS CodePipeline approve action
                elif sns.get("Subject") is not None:
                    body = approve_template(sns)

                else:
                    raise ValueError("Unknown message type.", sns)
            else:
                raise ValueError("Unknown message type.", sns)

            body.update({
                "channel": os.environ.get('CHANNEL'),
                "alias": "AWS Notification",
            })

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
