import urllib.request
import urllib.parse
import random

def sendSMS(numbers, message):
    apikey = 'NTU2NzdhNGY3OTUyNmM0ZjRmNDM0MjYxNzg2OTRjMzE='
    payload = {'apikey': apikey, 'numbers': numbers, 'message' : message, 'sender': 'TXTLCL'}
    data =  urllib.parse.urlencode(payload)
    data = data.encode('utf-8')
    request = urllib.request.Request("https://api.textlocal.in/send/?")
    f = urllib.request.urlopen(request, data)
    fr = f.read()
    return(fr)
 
resp =  sendSMS( '919985832472', f'Your OTP is : {random.randint(100000, 999999)}')
print (resp)