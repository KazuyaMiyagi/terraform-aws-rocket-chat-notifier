import os
import urllib.request
import json
from datetime import datetime, timezone, timedelta
from pprint import pprint

def lambda_handler(event, context):
    try:
        topic = event['Records'][0]['Sns']

        post = {}
        post["channel"] = os.environ.get('CHANNEL')
        post["alias"] = "AWS Notification"

        # Subscribe
        if topic.get("Type") == "SubscriptionConfirmation":
            post["icon_emoji"] = ":aws-sns:"

            post["text"] = """
            [{message}]({link})
            """.format(
                message=topic.get("Message"),
                link=topic.get("SubscribeURL"),
            )

        # Approve action
        elif topic.get("Subject") != None:
            post["icon_emoji"] = ":stop_sign:"

            message = json.loads(topic.get('Message'))
            expire = message.get('approval', {}).get('expires')

            jst = timezone(timedelta(hours=+9), 'JST')
            expire_jst = datetime.strptime(expire, '%Y-%m-%dT%H:%M%z').astimezone(jst)

            vst = timezone(timedelta(hours=+7), 'VST')
            expire_vst = datetime.strptime(expire, '%Y-%m-%dT%H:%M%z').astimezone(vst)

            post["text"] = """
            [{message}]({link})
            Expire(JST): {expire_jst}
            Expire(VST): {expire_vst}
            """.format(
                message=topic.get("Subject"),
                link=message.get("approval").get("approvalReviewLink"),
                expire_jst=str(expire_jst),
                expire_vst=str(expire_vst),
            )

        else:
            message = json.loads(topic.get('Message'))
            detail = message.get("detail")
            # AWS CodePipeline
            if message.get("source") == "aws.codepipeline":
                post["icon_emoji"] = ":aws-code-pipeline:"

                post["text"] = """
                {title}
                Pipeline: {pipeline}
                Stage: {stage}
                Action: {action}
                State: {state}
                """.format(
                    title=message.get("detailType"),
                    pipeline=detail.get("pipeline"),
                    stage=detail.get("stage"),
                    action=detail.get("action"),
                    state=detail.get("state"),
                )
            # AWS CodeBuild
            elif message.get("source") == "aws.codebuild":
                post["icon_emoji"] = ":aws-code-build:"

                post["text"] = """
                {title}
                ProjectName: {project_name}
                BuildStatus: {build_status}
                CurrentPhase: {current_phase}
                Initiator: {initiator}
                """.format(
                    title=message.get("detailType"),
                    project_name=detail.get("project-name"),
                    build_status=detail.get("build-status"),
                    current_phase=detail.get("current-phase"),
                    initiator=detail.get("additional-information").get("initiator"),
                )
            else:
                post["text"] = topic

        url = os.environ.get('WEBHOOK_URL')
        headers = {
            'Content-Type': 'application/json'
        }
        req = urllib.request.Request(url, json.dumps(post).encode(), headers)
        with urllib.request.urlopen(req) as res:
            body = res.read()
    except Exception as e:
        pprint(e)
        pprint(event)
        pprint(context)
