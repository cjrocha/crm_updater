import base64
import hashlib
import hmac
# Encoding (base64) and generating the API signature so that scrapper
# receives data from Unleashed API
def api_signature(message,api_key):
    message = bytes(message, 'utf-8')
    secret = bytes(api_key, 'utf-8')
    api_signature = base64.b64encode(hmac.new(secret, message, digestmod=hashlib.sha256).digest())
    return api_signature

if __name__ == "__main__":
    print( api_signature('') )
    print( api_signature('Message') )