import json
import logging
from botocore.vendored import requests

"""
You need to create new webhook in your chat,
and replace GOOGLE_WEBHOOK_URL by yours URL
"""

GOOGLE_WEBHOOK_URL = 'https://chat.googleapis.com/v1/spaces/########/messages?key=####################################&token=########################################'


def lambda_handler(event, context):
    
    logging.info("Event: " + str(event))
    
    for record in event["Records"]:
        if type(record["Sns"]["Message"]) == str:
            contents = json.loads(record["Sns"]["Message"])
        else:
            contents = record["Sns"]["Message"]
        
        message = "*" + contents["AlarmName"] + ":* " + contents["OldStateValue"] + " ⟶ " + contents["NewStateValue"] + "\n```" + contents["NewStateReason"] +"```"
        logging.info("Message to GoogleChat: " + str(message))
        
        bot_message = {'text': message}
        message_headers = {'Content-Type': 'application/json; charset=UTF-8'}
        
        response = requests.post(url=GOOGLE_WEBHOOK_URL, headers=message_headers, data=json.dumps(bot_message))
