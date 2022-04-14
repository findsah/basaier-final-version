import requests
import datetime
from django.http import HttpResponse

date = datetime.datetime.now().strftime("%Y-%m-%d")


def sendSMS(message, fromSender, toReciever):
    url = 'https://www.smsbox.com/SMSGateway/Services/Messaging.asmx/Http_SendSMS'
    stringNumber = str(toReciever)
    concatenatedNumber = '965{}'.format(stringNumber)
    # print("Concatednated Number", concatenatedNumber)
    print("Fetched Number", stringNumber)
    # url = 'https://www.smsbox.com/smsgateway/services/messaging.asmx/Http_SendSMS?username=basaier&password=S@basorg&customerid=1664&sendertext=SMSBOX.COM&messagebody=hello&recipientnumbers=96590900055&defdate=&isblink=false&isflash=false'
    payload = {
        "username": 'basaier',
        "password": 'S@basorg',
        "customerId": '1664',
        "senderText": 'Basaier.org',
        "messageBody": message,
        "recipientNumbers": stringNumber,
        'defdate': '',
        "isblink": 'false',
        "isflash": 'false',
    }
    response = requests.post(url, payload)
    # response = requests.post(url)
    print("RESPONSE FROM TOSENDSMS.PY FILE", message)
    print("RESPONSE FROM TOSENDSMS.PY FILE", HttpResponse.status_code)
    # print(url)
    return HttpResponse.status_code
