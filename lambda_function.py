import json
import logging
from botocore.vendored import requests
from pygelf import GelfUdpHandler


"""
Set your envs in lambda envinroment:
- GOOGLE_WEBHOOK_URL
- GRAYLOG_URL
- GRAYLOG_PORT
- GRAYLOG_TAG
"""


logging.getLogger().addHandler(GelfUdpHandler(
    host=os.environ['GRAYLOG_URL'],
    port=os.environ['GRAYLOG_PORT'],
    include_extra_fields=True,
    _facility='_facility',
    tag=os.environ['GRAYLOG_TAG']
))
google_chat_url = os.environ['GOOGLE_WEBHOOK_URL']


def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))

    try:
        text = get_text(get_message_from_event(event))
        send_to_chat(text, google_chat_url)
        logging.warning(f'message body: {event}')
        return {
            'statusCode': 200,
            'body': str(text)
        }

    except Exception as e:
        logging.error(f'Exception:{e}. Message{event}')
        return {
            'statusCode': 500,
            'body': 'Send ERROR to chat - ' + str(send_to_chat(f'Something went wrong with sns-to-googlechat:\n```{e}\n{event}```', google_chat_url))
        }


def get_message_from_event(event: dict) -> dict:
    return json.loads(event.get('Records')[0].get('Sns').get('Message'))


def get_text(message: dict) -> str:
    alarm_name = message['AlarmName'] if 'AlarmName' in message.keys() else ''
    old_state = message['OldStateValue'] if 'OldStateValue' in message.keys() else ''
    new_state = message['NewStateValue'] if 'NewStateValue' in message.keys() else ''
    new_state_reason = message['NewStateReason'] if 'NewStateReason' in message.keys() else ''

    return f'*{alarm_name}:* {old_state} ⟶ {new_state}\n```{new_state_reason}```'


def send_to_chat(text: str, webhook_url: str):
    message = {'text': text}
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    response = requests.post(url=webhook_url, headers=headers, data=json.dumps(message))

    if response.status_code != 200:
        return False

    return True

