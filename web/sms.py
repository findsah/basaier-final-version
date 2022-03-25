import requests
from django.conf import settings


def sendSMS(message, fromm, to):
    url = 'https://www.smsbox.com/SMSGateway/Services/Messaging.asmx/Http_SendSMS'
    payload = {
        "username": settings.SMSUsername,
        "password": settings.SMSPassword,
        "customerId": settings.SMSCutomerID,
        "senderText": settings.SMSSenderName,
        "messageBody": str(message),
        "recipientNumbers": ','.join(to),
        "isBlink": False,
        "isFlash": False
    }
    response = requests.post(url, payload)
