import json
import traceback

import requests

BODY_TPL = """Hi Everyone,
There's been an error in an airflow task.
DAG ID: {dag_id}
TASK ID: {task_id}
EXECUTION DATE: {execution_date}
LOG URL : {log_url}
EXCEPTION MESSAGE: {exception}
TRACEBACK:
=============================
{traceback}
=============================
Forever yours,
Airflow bot"""


def email_notifier(sender_name, sender_email, recipients, api_key, api_secret):

    recipients = recipients.split(",")

    def notify(context, **kwargs):
        """Send custom email alerts."""
        print('context', str(context))

        task_instance = context['task_instance']

        subject = "Airflow Failure on {dag_id}.{task_id}".format(
            dag_id=task_instance.dag_id,
            task_id=task_instance.task_id
        )
        message_args = {
            'exception': context['exception'],
            'traceback': traceback.format_exc(),
            'task_id': task_instance.task_id,
            'dag_id': task_instance.dag_id,
            'execution_date': task_instance.execution_date,
            'log_url': task_instance.log_url,
            'log_filepath': task_instance.log_filepath
        }
        body = BODY_TPL.format(**message_args)

        sender_info = {"Email": sender_email, "Name": sender_name}
        bcc_recipients = []
        data = {"Messages": [{
            "From": sender_info,
            "To": [{"Email": recipient} for recipient in recipients],
            "Bcc": [{"Email": bcc_recipient} for bcc_recipient in bcc_recipients],
            "Subject": subject,
            "Attachments": [],
            "TextPart": body,
        }]}
        response = requests.post(
            'https://api.mailjet.com/v3.1/send',
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'},
            auth=(
                api_key,
                api_secret
            )
        )
        if response.status_code != 200:
            raise RuntimeError(str(json.loads(response.json())))

    return notify