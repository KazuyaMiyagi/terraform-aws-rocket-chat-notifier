from datetime import datetime, timezone, timedelta
from string import Template
from pprint import pprint
import json
import os
import urllib.request


ICONS = {
    "sns": "https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/main/dist/ApplicationIntegration/SNS.png",
    "codepipeline": "https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/main/dist/DeveloperTools/CodePipeline.png",
    "codebuild": "https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/main/dist/DeveloperTools/CodeBuild.png",
    "user": "https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/main/dist/General/User.png",
}


def subscribe_template(sns):
    tpl = """${Message}
    [Link](${SubscribeURL})"""
    params = {
        "Message": sns.get("Message"),
        "SubscribeURL": sns.get("SubscribeURL"),
    }
    return {
        "avatar": ICONS.get("sns"),
        "text": Template(tpl).substitute(**params),
    }


def codepipeline_template(sns):
    message = json.loads(sns.get("Message"))
    tpl = """${detailType}
    Pipeline: ${pipeline}
    Stage: ${stage}
    Action: ${action}
    State: ${state}"""
    params = {
        "detailType": message.get("detailType"),
        "pipeline": message.get("detail").get("pipeline"),
        "stage": message.get("detail").get("stage"),
        "action": message.get("detail").get("action"),
        "state": message.get("detail").get("state"),
    }
    return {
        "avatar": ICONS.get("codepipeline"),
        "text": Template(tpl).substitute(**params),
    }


def codebuild_template(sns):
    message = json.loads(sns.get("Message"))
    tpl = """${detailType}
    ProjectName: ${project_name}
    BuildStatus: ${build_status}
    CurrentPhase: ${current_phase}
    Initiator: ${initiator}"""
    params = {
        "detailType": message.get("detailType"),
        "project_name": message.get("detail").get("project-name"),
        "build_status": message.get("detail").get("build-status"),
        "current_phase": message.get("detail").get("current-phase"),
        "initiator": message.get("detail").get("additional-information").get("initiator"),
    }
    return {
        "avatar": ICONS.get("codebuild"),
        "text": Template(tpl).substitute(**params),
    }


def approve_template(sns):
    message = json.loads(sns.get("Message"))
    jst = timezone(timedelta(hours=+9), 'JST')
    expire = message.get('approval', {}).get('expires')
    expire_jst = str(datetime.strptime(expire, '%Y-%m-%dT%H:%M%z').astimezone(jst))

    tpl = """${Subject}
    ${approvalReviewLink}
    Expire: ${expire_jst}"""
    params = {
        "Subject": sns.get("Subject"),
        "approvalReviewLink": message.get("approval").get("approvalReviewLink"),
        "expire_jst": expire_jst,
    }

    return {
        "avatar": ICONS.get("user"),
        "text": Template(tpl).substitute(**params),
    }


def unknown_template(sns):
    tpl = """Unknown message type.
    ```
    ${sns}
    ```"""
    params = {
        "sns": sns,
    }
    return {
        "text": Template(tpl).substitute(**params),
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
                body = unknown_template(sns)

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

    except Exception as e:
        pprint(e)
        pprint(event)
        pprint(context)
